import asyncio
import io
import json
import os
import time
import logging
import wave
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
from dotenv import load_dotenv

from fastapi import APIRouter, Request, HTTPException, File, UploadFile, Form, Header, FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
EMAIL = os.environ.get("MEROSS_EMAIL")
PASSWORD = os.environ.get("MEROSS_PASSWORD")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

print(f"API key loaded (last 4 chars): ...{OPENAI_API_KEY[-4:]}")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up proxy if needed
if os.getenv('HTTPS_PROXY'):
    os.environ['OPENAI_PROXY'] = os.getenv('HTTPS_PROXY')

# Audio storage directory
AUDIO_STORAGE_DIR = Path(os.environ.get("OMI_AUDIO_DIR", Path.cwd() / "voice_audio")).resolve()
try:
    AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Audio storage directory ready at {AUDIO_STORAGE_DIR}")
except Exception as exc:
    logger.error(f"Failed to prepare audio storage directory {AUDIO_STORAGE_DIR}: {exc}")

# Create router
router = APIRouter(tags=["meross-device"])

# Track startup time
start_time = time.time()


# Pydantic models
class OMISegment(BaseModel):
    id: str
    text: str
    speaker: str
    speaker_id: int
    is_user: bool
    person_id: Optional[str] = None
    start: float
    end: float
    translations: List[str] = []
    speech_profile_processed: bool = False


class OMIWebhookRequest(BaseModel):
    session_id: str
    segments: List[OMISegment] = []
    uid: Optional[str] = None


class OMIWebhookResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None


class LightControlResponse(BaseModel):
    status: str
    message: str


class VoiceCommandResponse(BaseModel):
    status: str
    transcript: Optional[str] = None
    intent: Optional[Dict[str, str]] = None
    deviceAction: Optional[Dict[str, Any]] = None
    audioFilePath: Optional[str] = None


class StatusResponse(BaseModel):
    message: str
    endpoints: Dict[str, str]
    credentialsConfigured: bool


class CredentialsRequest(BaseModel):
    email: str
    password: str


class CredentialsResponse(BaseModel):
    status: str
    message: str


# Helper functions
def credentials_configured() -> bool:
    """Return True when Meross credentials are ready to use."""
    ready = bool(EMAIL and PASSWORD)
    logger.debug(f"credentials_configured -> {ready}")
    return ready


async def get_device():
    """Get the device for each request"""
    if not credentials_configured():
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not configured. Set MEROSS_EMAIL and MEROSS_PASSWORD environment variables."
        )

    logger.debug("Creating Meross HTTP client")
    http_api_client = await MerossHttpClient.async_from_user_password(
        email=EMAIL, password=PASSWORD, api_base_url="https://iot.meross.com"
    )
    
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    
    logger.debug("Running Meross device discovery")
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss110")
    
    if len(plugs) < 1:
        raise HTTPException(status_code=404, detail="No mss110 plugs found")

    device = plugs[0]
    logger.debug(f"Selected device {device.uuid} ({device.name})")
    await device.async_update()
    
    return manager, http_api_client, device


async def cleanup(manager, http_api_client):
    """Clean up connections"""
    try:
        manager.close()
        await http_api_client.async_logout()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


async def turn_on_light() -> Tuple[bool, str]:
    """Turn on the light"""
    manager, http_api_client, device = await get_device()
    try:
        await device.async_turn_on(channel=0)
        return True, f"Turned on {device.name}"
    finally:
        await cleanup(manager, http_api_client)


async def turn_off_light() -> Tuple[bool, str]:
    """Turn off the light"""
    manager, http_api_client, device = await get_device()
    try:
        await device.async_turn_off(channel=0)
        return True, f"Turned off {device.name}"
    finally:
        await cleanup(manager, http_api_client)


def save_audio_debug_file(audio_bytes: bytes, filename_hint: str, sample_rate: int) -> Optional[Path]:
    """
    Persist audio bytes as WAV for debugging and return the saved path.
    On serverless platforms, saves to /tmp directory if available.
    Returns None if file saving is not available.
    """
    # On serverless (Vercel), use /tmp directory which is writable
    # On local/dev, use configured directory
    if os.path.exists("/tmp") and os.access("/tmp", os.W_OK):
        storage_dir = Path("/tmp")
    elif AUDIO_STORAGE_DIR.exists() and AUDIO_STORAGE_DIR.is_dir():
        storage_dir = AUDIO_STORAGE_DIR
    else:
        # Try to create the directory
        try:
            AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            storage_dir = AUDIO_STORAGE_DIR
        except Exception:
            # If we can't create directory, skip file saving (serverless)
            logger.debug("Cannot save audio file - no writable directory available")
            return None
    
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    safe_name = Path(filename_hint).stem or "omi-audio"
    destination = storage_dir / f"{timestamp}_{safe_name}.wav"

    try:
        with wave.open(destination, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_bytes)
        logger.debug(f"Saved audio payload to {destination}")
        return destination
    except Exception as exc:
        logger.error(f"Failed to save WAV file {destination}: {exc}")
        # Try fallback: dump raw bytes
        try:
            raw_destination = destination.with_suffix('.raw')
            raw_destination.write_bytes(audio_bytes)
            logger.debug(f"Saved raw audio payload to {raw_destination}")
            return raw_destination
        except Exception:
            logger.debug("Cannot save audio file - filesystem error")
            return None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def transcribe_audio_payload(audio_bytes: bytes, filename: str = "omi-audio.wav") -> str:
    """Run Whisper transcription on uploaded audio."""
    if not audio_bytes:
        logger.error("Uploaded audio payload empty")
        raise ValueError("Audio file is empty.")

    logger.debug(f"Received audio payload {filename} with {len(audio_bytes)} bytes")
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = filename or "omi-audio.wav"
    audio_stream.seek(0)

    logger.debug("Sending audio to Whisper")
    try:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream,
            response_format="text"
        )
        text = transcription.strip()
        logger.debug(f"Whisper transcript: {text}")
        return text
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise


INTENT_PROMPT = (
    "You are Omi, a helpful smart-home assistant. "
    "Given a user's speech transcript, decide if they want to control the coffee machine or room light. "
    "Respond with strict JSON containing: action ('turn_on', 'turn_off', or 'none'), device ('coffee machine', 'room light', or ''), "
    "assistant_message (what you will say back to the user), and follow_up (any short suggestion or question). "
    "Infer intent even if indirect (e.g., tired -> coffee machine on, too dark -> room light on). "
    "If unsure, set action to 'none' and ask a clarifying question."
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def infer_intent_from_transcript(transcript: str) -> Dict[str, str]:
    """Use GPT to convert transcript into a structured intent."""
    logger.debug(f"Sending transcript to GPT intent model: {transcript}")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": INTENT_PROMPT,
                },
                {
                    "role": "user",
                    "content": transcript,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "omi_intent",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["turn_on", "turn_off", "none"],
                            },
                            "device": {
                                "type": "string",
                                "description": "Target device name."
                            },
                            "assistant_message": {
                                "type": "string",
                                "description": "What the assistant says back to the user."
                            },
                            "follow_up": {
                                "type": "string",
                                "description": "Optional follow-up, may be empty."
                            }
                        },
                        "required": ["action", "device", "assistant_message", "follow_up"],
                        "additionalProperties": False
                    }
                }
            },
            temperature=0.7,
            timeout=30,
        )

        # Parse the JSON response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        payload = json.loads(content)
        logger.debug(f"Parsed intent payload: {payload}")
        return payload
    except json.JSONDecodeError as exc:
        logger.error(f"Failed to parse intent JSON: {exc}")
        raise ValueError("Intent parsing failed") from exc
    except Exception as e:
        logger.error(f"Error inferring intent: {e}")
        raise


DEVICE_KEYWORDS = {
    "coffee": "coffee machine",
    "coffee machine": "coffee machine",
    "light": "room light",
    "room light": "room light",
    "lamp": "room light",
}


def resolve_device_name(raw_name: str) -> Optional[str]:
    """Map free-text device name to a supported device label."""
    name = (raw_name or "").lower()
    logger.debug(f"Resolving device name from '{raw_name}'")
    for keyword, canonical in DEVICE_KEYWORDS.items():
        if keyword in name:
            logger.debug(f"Device resolved to {canonical}")
            return canonical
    logger.debug("No matching device found")
    return None


async def perform_device_action(device_name: str, action: str) -> Tuple[bool, str]:
    """Execute the requested Meross action if supported."""
    canonical = resolve_device_name(device_name)
    if canonical is None:
        return False, f"I don't recognise the device '{device_name}'."

    if action == "turn_on":
        logger.debug(f"Performing turn_on for {canonical}")
        success, message = await turn_on_light()
    elif action == "turn_off":
        logger.debug(f"Performing turn_off for {canonical}")
        success, message = await turn_off_light()
    else:
        logger.debug("Unsupported action requested")
        return False, "No action executed."

    if canonical == "coffee machine" and success:
        return True, "Coffee machine powered on."

    if canonical == "room light" and action == "turn_on" and success:
        return True, "Room light switched on."

    if canonical == "room light" and action == "turn_off" and success:
        return True, "Room light switched off."

    return success, message


def extract_text_from_segments(segments: List[OMISegment]) -> str:
    """Extract and combine text from OMI segments."""
    if not segments:
        return ""
    
    # Filter to user segments only and combine text
    user_segments = [seg.text for seg in segments if seg.is_user]
    return " ".join(user_segments).strip()


# API Routes
@router.post("/webhook", response_model=OMIWebhookResponse)
async def omi_webhook(request: OMIWebhookRequest):
    """
    OMI webhook endpoint for receiving real-time transcripts.
    
    Processes speech transcripts from OMI device, infers device control intents,
    and executes Meross device actions when appropriate.
    """
    logger.info(f"Received OMI webhook request for session_id: {request.session_id}")
    logger.debug(f"Received data: {request.dict()}")
    
    if not request.session_id:
        raise HTTPException(status_code=400, detail="No session_id provided")
    
    # Extract transcript from segments
    transcript = extract_text_from_segments(request.segments)
    
    if not transcript:
        logger.debug("No transcript text found in segments")
        return OMIWebhookResponse(status="success", message=None)
    
    logger.info(f"Processing transcript: '{transcript}'")
    
    # Infer intent from transcript
    try:
        intent = infer_intent_from_transcript(transcript)
    except ValueError as err:
        logger.error(f"OpenAI configuration error: {err}")
        return OMIWebhookResponse(
            status="success",
            message="I'm having trouble understanding your request right now."
        )
    except Exception as err:
        logger.error(f"Intent inference failed: {err}")
        return OMIWebhookResponse(
            status="success",
            message="I couldn't analyze that request. Please try again."
        )
    
    logger.debug(f"Intent result: {intent}")
    
    # Execute device action if applicable
    response_message = intent.get("assistant_message", "")
    
    if intent.get("action") in {"turn_on", "turn_off"} and credentials_configured():
        try:
            success, device_message = await perform_device_action(
                intent.get("device", ""), intent["action"]
            )
            if success:
                response_message = device_message
            else:
                response_message = device_message or response_message
        except Exception as err:
            logger.error(f"Error executing device action: {err}")
            response_message = "I had trouble controlling the device. Please try again."
    elif intent.get("action") in {"turn_on", "turn_off"} and not credentials_configured():
        response_message = "Meross credentials are not configured. Please set MEROSS_EMAIL and MEROSS_PASSWORD environment variables."
    
    # Add follow-up if present
    if intent.get("follow_up"):
        response_message = f"{response_message} {intent.get('follow_up')}"
    
    logger.info(f"Responding with: {response_message}")
    
    return OMIWebhookResponse(
        status="success",
        message=response_message
    )


@router.get("/webhook/setup-status")
async def webhook_setup_status():
    """Check if webhook setup is complete."""
    try:
        return {"is_setup_completed": True}
    except Exception as e:
        logger.error(f"Error checking setup status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/on", response_model=LightControlResponse)
async def light_on():
    """Turn light on"""
    if not credentials_configured():
        raise HTTPException(
            status_code=401,
            detail="Please set MEROSS_EMAIL and MEROSS_PASSWORD environment variables to configure Meross credentials."
        )

    try:
        success, message = await turn_on_light()
        if success:
            return LightControlResponse(status="success", message=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error turning on light: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/off", response_model=LightControlResponse)
async def light_off():
    """Turn light off"""
    if not credentials_configured():
        raise HTTPException(
            status_code=401,
            detail="Please set MEROSS_EMAIL and MEROSS_PASSWORD environment variables to configure Meross credentials."
        )

    try:
        success, message = await turn_off_light()
        if success:
            return LightControlResponse(status="success", message=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error turning off light: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice", response_model=VoiceCommandResponse)
async def handle_voice_command(
    request: Request,
    audio: Optional[UploadFile] = File(None),
    x_audio_filename: Optional[str] = Header(None, alias="X-Audio-Filename"),
    x_audio_sample_rate: Optional[str] = Header(None, alias="X-Audio-Sample-Rate"),
):
    """Process voice input: transcribe, infer intent, execute device action."""
    audio_bytes: bytes = b""
    filename = "omi-audio.wav"

    # Check for multipart file upload
    if audio:
        filename = audio.filename or filename
        audio_bytes = await audio.read()
        logger.debug(f"/voice received multipart file field 'audio' -> {filename}")
    else:
        # Try to read raw body
        try:
            audio_bytes = await request.body()
            filename = x_audio_filename or filename
            logger.debug(f"/voice received raw body audio -> {filename}")
        except Exception as e:
            logger.error(f"Error reading request body: {e}")

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Provide audio via multipart 'audio' field or raw body."
        )

    # Get sample rate
    sample_rate = x_audio_sample_rate or request.query_params.get('sample_rate', '16000')
    try:
        sample_rate_int = int(sample_rate)
    except (TypeError, ValueError):
        sample_rate_int = 16000

    saved_path = save_audio_debug_file(audio_bytes, filename, sample_rate_int)

    # Transcribe audio
    try:
        transcript = transcribe_audio_payload(audio_bytes, filename)
    except ValueError as err:
        logger.error(f"Voice command failed, configuration missing: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as err:
        logger.error(f"Unable to transcribe audio: {err}")
        raise HTTPException(status_code=500, detail="Transcription failed.")

    # Infer intent
    try:
        intent = infer_intent_from_transcript(transcript)
    except ValueError as err:
        logger.error(f"OpenAI configuration error: {err}")
        raise HTTPException(status_code=500, detail=str(err))
    except Exception as err:
        logger.error(f"Intent inference failed: {err}")
        raise HTTPException(status_code=500, detail="Intent analysis failed.")

    action_result: Dict[str, Optional[str]] = {
        "executed": False,
        "device": intent.get("device"),
        "message": None,
    }

    logger.debug(f"Intent result: {intent}")
    if intent.get("action") in {"turn_on", "turn_off"} and credentials_configured():
        try:
            success, device_message = await perform_device_action(
                intent.get("device", ""), intent["action"]
            )
            action_result["executed"] = success
            action_result["message"] = device_message
        except Exception as err:
            logger.error(f"Error executing device action: {err}")
            action_result["message"] = "Device action failed."
    elif intent.get("action") in {"turn_on", "turn_off"} and not credentials_configured():
        action_result["message"] = "Meross credentials missing. Set MEROSS_EMAIL and MEROSS_PASSWORD environment variables."

    return VoiceCommandResponse(
        status="success",
        transcript=transcript,
        intent=intent,
        deviceAction=action_result,
        audioFilePath=str(saved_path) if saved_path else None,
    )


@router.get("/", response_model=StatusResponse)
async def home():
    """Home page"""
    return StatusResponse(
        message="OMI Meross Device Controller",
        endpoints={
            "GET /on": "Turn light on",
            "GET /off": "Turn light off",
            "POST /voice": "Transcribe audio and control devices",
            "POST /webhook": "OMI webhook endpoint for real-time transcripts"
        },
        credentialsConfigured=credentials_configured()
    )


@router.get("/status")
async def status():
    """Get service status"""
    return {
        "active": True,
        "uptime": time.time() - start_time,
        "credentials_configured": credentials_configured()
    }


# Create FastAPI app instance
app = FastAPI(
    title="OMI Meross Device Controller",
    description="Smart home device controller for Meross devices",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
