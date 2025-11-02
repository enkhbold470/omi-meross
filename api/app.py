import asyncio
import io
import json
import os
import time
import logging
import wave
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any
from dotenv import load_dotenv

from fastapi import APIRouter, Request, HTTPException, File, UploadFile, Form, Header, FastAPI, Cookie
from fastapi.responses import JSONResponse, HTMLResponse, Response, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
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
# On Vercel/serverless, default to /tmp (ephemeral storage)
# On local/dev, use configured directory or default to voice_audio in current dir
if os.path.exists("/tmp") and os.access("/tmp", os.W_OK):
    default_storage = Path("/tmp") / "voice_audio"
else:
    default_storage = Path.cwd() / "voice_audio"

AUDIO_STORAGE_DIR = Path(os.environ.get("OMI_AUDIO_DIR", str(default_storage))).resolve()
try:
    # Only try to create directory if it's not /tmp (which always exists)
    if str(AUDIO_STORAGE_DIR).startswith("/tmp"):
        # Just ensure the subdirectory exists in /tmp
        if AUDIO_STORAGE_DIR != Path("/tmp"):
            AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audio storage directory ready at {AUDIO_STORAGE_DIR} (serverless)")
    else:
        AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Audio storage directory ready at {AUDIO_STORAGE_DIR}")
except Exception as exc:
    logger.warning(f"Failed to prepare audio storage directory {AUDIO_STORAGE_DIR}: {exc}. Will use /tmp if available.")

# Create router
router = APIRouter(tags=["meross-device"])

# Templates for HTML responses
template_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(template_dir))

# Track startup time
start_time = time.time()

# Thread-safe user credential storage
# Format: {uid: {"email": str, "password": str}}
_user_credentials: Dict[str, Dict[str, str]] = {}
_credentials_lock = threading.Lock()


def get_user_credentials(uid: str) -> Optional[Tuple[str, str]]:
    """Get credentials for a specific user."""
    with _credentials_lock:
        creds = _user_credentials.get(uid)
        if creds:
            return creds.get("email"), creds.get("password")
    return None


def set_user_credentials(uid: str, email: str, password: str):
    """Store credentials for a specific user."""
    with _credentials_lock:
        _user_credentials[uid] = {"email": email, "password": password}
    logger.info(f"Stored credentials for user {uid}")


def has_user_credentials(uid: str) -> bool:
    """Check if user has credentials configured."""
    with _credentials_lock:
        return uid in _user_credentials and bool(_user_credentials[uid].get("email") and _user_credentials[uid].get("password"))


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


class DeviceInfo(BaseModel):
    uuid: str
    name: str
    type: str
    online: bool = True


class DeviceListResponse(BaseModel):
    status: str
    devices: List[DeviceInfo]
    count: int


class DeviceSelectionRequest(BaseModel):
    device_uuid: str


class DeviceSelectionResponse(BaseModel):
    status: str
    message: str
    device_uuid: Optional[str] = None
    device_name: Optional[str] = None


class CredentialsRequest(BaseModel):
    email: str
    password: str


class CredentialsResponse(BaseModel):
    status: str
    message: str


# Helper functions
def credentials_configured(email: Optional[str] = None, password: Optional[str] = None) -> bool:
    """Return True when Meross credentials are ready to use."""
    ready = bool(email and password)
    logger.debug(f"credentials_configured -> {ready}")
    return ready


async def get_all_devices(email: str, password: str):
    """Get all devices from Meross account."""
    if not email or not password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not provided. Please log in at /login"
        )

    logger.debug("Creating Meross HTTP client")
    http_api_client = await MerossHttpClient.async_from_user_password(
        email=email, password=password, api_base_url="https://iot.meross.com"
    )
    
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    
    logger.debug("Running Meross device discovery")
    await manager.async_device_discovery()
    
    # Get all devices (not just mss110)
    all_devices = manager.find_devices()
    
    return manager, http_api_client, all_devices


async def get_device(email: str, password: str, device_uuid: Optional[str] = None):
    """Get a specific device by UUID, or first available device if UUID not provided."""
    manager, http_api_client, all_devices = await get_all_devices(email, password)
    
    if not all_devices or len(all_devices) < 1:
        await cleanup(manager, http_api_client)
        raise HTTPException(status_code=404, detail="No devices found in Meross account")
    
    # If device UUID specified, find it
    if device_uuid:
        device = next((d for d in all_devices if d.uuid == device_uuid), None)
        if not device:
            await cleanup(manager, http_api_client)
            raise HTTPException(status_code=404, detail=f"Device {device_uuid} not found")
    else:
        # Use first device as default
        device = all_devices[0]
    
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


async def turn_on_device(email: str, password: str, device_uuid: Optional[str] = None) -> Tuple[bool, str]:
    """Turn on the device"""
    manager, http_api_client, device = await get_device(email, password, device_uuid)
    try:
        await device.async_turn_on(channel=0)
        return True, f"Turned on {device.name}"
    finally:
        await cleanup(manager, http_api_client)


async def turn_off_device(email: str, password: str, device_uuid: Optional[str] = None) -> Tuple[bool, str]:
    """Turn off the device"""
    manager, http_api_client, device = await get_device(email, password, device_uuid)
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
    "Given a user's speech transcript, extract the device name or room name from what they say "
    "(e.g., 'bedroom', 'kitchen', 'living room', 'office', etc.). "
    "If no specific device or room is mentioned, leave device as empty string (it will default to 'Living Room'). "
    "Respond with strict JSON containing: action ('turn_on', 'turn_off', or 'none'), "
    "device (the room/device name from the transcript, or empty string for default), "
    "assistant_message (what you will say back to the user), and follow_up (any short suggestion or question). "
    "Infer intent even if indirect (e.g., 'too dark' -> room light on, 'turn off bedroom' -> bedroom device off). "
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
                                "description": "Device or room name from the transcript (e.g., 'bedroom', 'kitchen', 'living room'). Leave empty if not specified (defaults to 'Living Room')."
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


def find_device_by_name(device_name: str, devices: List[Any]) -> Optional[Any]:
    """Find a device by matching its name (case-insensitive, partial match)."""
    if not device_name or not devices:
        return None
    
    device_name_lower = device_name.lower().strip()
    logger.debug(f"Searching for device matching '{device_name}' among {len(devices)} devices")
    
    # Try exact match first
    for device in devices:
        if device.name and device.name.lower() == device_name_lower:
            logger.debug(f"Exact match found: {device.name}")
            return device
    
    # Try partial match (device name contains the search term or vice versa)
    for device in devices:
        if device.name:
            device_lower = device.name.lower()
            if device_name_lower in device_lower or device_lower in device_name_lower:
                logger.debug(f"Partial match found: {device.name}")
                return device
    
    # Try matching room names (e.g., "bedroom" matches "Bedroom Light")
    words = device_name_lower.split()
    for device in devices:
        if device.name:
            device_words = device.name.lower().split()
            if any(word in device_words for word in words if len(word) > 2):
                logger.debug(f"Room name match found: {device.name}")
                return device
    
    logger.debug("No matching device found")
    return None


def get_default_device(devices: List[Any]) -> Optional[Any]:
    """Get the default device (Living Room) or first available device."""
    if not devices:
        return None
    
    # Try to find "Living Room" (case-insensitive)
    living_room = find_device_by_name("Living Room", devices)
    if living_room:
        logger.debug(f"Using default device: {living_room.name}")
        return living_room
    
    # Fallback to first device
    if devices:
        logger.debug(f"No 'Living Room' found, using first device: {devices[0].name}")
        return devices[0]
    
    return None


async def perform_device_action(device_name: str, action: str, email: str, password: str, device_uuid: Optional[str] = None) -> Tuple[bool, str]:
    """Execute the requested Meross action. Finds device by name if device_uuid not provided."""
    # If device_uuid is provided, use it directly
    if device_uuid:
        logger.debug(f"Using provided device UUID: {device_uuid}")
        if action == "turn_on":
            success, message = await turn_on_device(email, password, device_uuid)
        elif action == "turn_off":
            success, message = await turn_off_device(email, password, device_uuid)
        else:
            return False, "Unsupported action."
        return success, message
    
    # Otherwise, fetch devices and find by name
    manager, http_api_client, devices = None, None, None
    try:
        manager, http_api_client, devices = await get_all_devices(email, password)
        
        if not devices:
            return False, "No devices found in your Meross account."
        
        # Find device by name
        target_device = None
        if device_name:
            target_device = find_device_by_name(device_name, devices)
        
        # If not found, use default (Living Room)
        if not target_device:
            target_device = get_default_device(devices)
            if not target_device:
                return False, "No devices available."
            
            if device_name:
                logger.info(f"Device '{device_name}' not found, using default device: {target_device.name}")
            else:
                logger.info(f"No device specified, using default device: {target_device.name}")
        
        # Execute action on the selected device
        device_uuid = target_device.uuid
        if action == "turn_on":
            success, message = await turn_on_device(email, password, device_uuid)
        elif action == "turn_off":
            success, message = await turn_off_device(email, password, device_uuid)
        else:
            return False, "Unsupported action."
        
        return success, message
    finally:
        if manager and http_api_client:
            await cleanup(manager, http_api_client)


def extract_text_from_segments(segments: List[OMISegment]) -> str:
    """Extract and combine text from OMI segments."""
    if not segments:
        return ""
    
    # Filter to user segments only and combine text
    user_segments = [seg.text for seg in segments if seg.is_user]
    return " ".join(user_segments).strip()


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # /vercel.svg is automatically served when included in the public/** directory.
    return RedirectResponse("/vercel.svg", status_code=307)

# API Routes
@router.get("/devices", response_class=HTMLResponse)
async def devices_page(
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password")
):
    """Device selection page. Shows list of devices and allows control."""
    if not meross_email or not meross_password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "uid": ""
            }
        )
    
    try:
        manager, http_api_client, device_list = await get_all_devices(meross_email, meross_password)
        try:
            devices = []
            for device in device_list:
                try:
                    await device.async_update()
                    devices.append({
                        "uuid": device.uuid,
                        "name": device.name,
                        "type": device.type,
                        "online": device.online
                    })
                except Exception:
                    devices.append({
                        "uuid": device.uuid,
                        "name": device.name or "Unknown",
                        "type": device.type or "Unknown",
                        "online": False
                    })
            
            selected_uuid = request.cookies.get("meross_device_uuid")
            
            return templates.TemplateResponse(
                "devices.html",
                {
                    "request": request,
                    "devices": devices,
                    "selected_uuid": selected_uuid
                }
            )
        finally:
            await cleanup(manager, http_api_client)
    except Exception as e:
        logger.error(f"Error loading devices: {e}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "uid": ""
            }
        )


@router.get("/devices/list", response_model=DeviceListResponse)
async def list_devices_api(
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password"),
    uid: Optional[str] = Cookie(None, alias="meross_uid")
):
    """API endpoint to list all devices from the user's Meross account."""
    email = meross_email
    password = meross_password
    
    # Fallback to server-side storage if no cookies
    if not email or not password:
        if uid:
            user_creds = get_user_credentials(uid)
            if user_creds:
                email, password = user_creds
    
    if not email or not password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not configured. Please log in at /login"
        )
    
    try:
        manager, http_api_client, devices = await get_all_devices(email, password)
        try:
            device_list = []
            for device in devices:
                try:
                    await device.async_update()
                    device_list.append(DeviceInfo(
                        uuid=device.uuid,
                        name=device.name,
                        type=device.type,
                        online=device.online
                    ))
                except Exception as e:
                    logger.error(f"Error updating device {device.uuid}: {e}")
                    device_list.append(DeviceInfo(
                        uuid=device.uuid,
                        name=device.name or "Unknown",
                        type=device.type or "Unknown",
                        online=False
                    ))
            
            return DeviceListResponse(
                status="success",
                devices=device_list,
                count=len(device_list)
            )
        finally:
            await cleanup(manager, http_api_client)
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, uid: Optional[str] = None):
    """Serve login page for setting Meross credentials."""
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "uid": uid or ""
        }
    )


@router.post("/login")
async def login(
    request: Request,
    uid: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission and store user credentials."""
    if not email or not password:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "uid": uid,
                "email": email,
                "error": "Email and password are required.",
            }
        )
    
    # Test credentials by trying to get devices
    try:
        manager, http_api_client, devices = await get_all_devices(email, password)
        await cleanup(manager, http_api_client)
        
        # Store credentials for this user
        set_user_credentials(uid, email, password)
        
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "uid": uid,
                "email": email,
                "error": None,
                "success": True
            }
        )
    except Exception as e:
        logger.error(f"Error validating credentials: {e}")
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "uid": uid,
                "email": email,
                "error": f"Invalid credentials or connection error: {str(e)}"
            }
        )


@router.post("/api/login", response_model=CredentialsResponse)
async def api_login(
    credentials: CredentialsRequest,
    request: Request,
    uid: Optional[str] = Cookie(None, alias="meross_uid")
):
    """API endpoint for setting credentials via JSON. Sets cookies."""
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Test credentials
    try:
        manager, http_api_client, devices = await get_all_devices(credentials.email, credentials.password)
        await cleanup(manager, http_api_client)
        
        # Create response with cookies
        response = JSONResponse({
            "status": "success",
            "message": "Credentials saved successfully"
        })
        
        # Set cookies (expires in 1 year)
        from datetime import timedelta
        expiry = timedelta(days=365)
        response.set_cookie(
            key="meross_email",
            value=credentials.email,
            max_age=int(expiry.total_seconds()),
            httponly=True,
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )
        response.set_cookie(
            key="meross_password",
            value=credentials.password,
            max_age=int(expiry.total_seconds()),
            httponly=True,
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )
        
        # Also store in server-side storage for webhook (if uid available)
        if uid:
            set_user_credentials(uid, credentials.email, credentials.password)
            response.set_cookie(
                key="meross_uid",
                value=uid,
                max_age=int(expiry.total_seconds()),
                httponly=True,
                samesite="lax",
                secure=False
            )
        
        return response
    except Exception as e:
        logger.error(f"Error validating credentials: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}")


@router.post("/webhook", response_model=OMIWebhookResponse)
async def omi_webhook(webhook_request: OMIWebhookRequest, request: Request):
    """
    OMI webhook endpoint for receiving real-time transcripts.
    
    Processes speech transcripts from OMI device, infers device control intents,
    and executes Meross device actions when appropriate.
    """
    logger.info(f"Received OMI webhook request for session_id: {webhook_request.session_id}, uid: {webhook_request.uid}")
    logger.debug(f"Received data: {webhook_request.dict()}")
    
    if not webhook_request.session_id:
        raise HTTPException(status_code=400, detail="No session_id provided")
    
    # Get user ID (use uid from request or fallback to session_id)
    uid = webhook_request.uid or webhook_request.session_id
    logger.debug(f"Processing request for uid: {uid}")
    
    # Get user credentials from cookies (if available) or server storage
    meross_email = request.cookies.get("meross_email")
    meross_password = request.cookies.get("meross_password")
    meross_device_uuid = request.cookies.get("meross_device_uuid")
    
    # Try cookies first, then fallback to server storage
    if meross_email and meross_password:
        email, password = meross_email, meross_password
        has_creds = True
        device_uuid = meross_device_uuid
    else:
        # Fallback to server-side storage
        user_creds = get_user_credentials(uid)
        email, password = user_creds if user_creds else (None, None)
        has_creds = has_user_credentials(uid)
        device_uuid = None
    
    # Extract transcript from segments
    transcript = extract_text_from_segments(webhook_request.segments)
    
    if not transcript:
        logger.debug("No transcript text found in segments")
        # If no credentials, prompt user to configure
        if not has_creds:
            setup_message = f"Please configure your Meross credentials at: /login?uid={uid}"
            return OMIWebhookResponse(status="success", message=setup_message)
        return OMIWebhookResponse(status="success", message=None)
    
    logger.info(f"Processing transcript: '{transcript}'")
    
    # Check if user is asking to set up/configure credentials
    if any(phrase in transcript.lower() for phrase in ["set up", "configure", "login", "credentials", "connect"]):
        setup_message = f"Please visit /login?uid={uid} to configure your Meross account."
        return OMIWebhookResponse(status="success", message=setup_message)
    
    # Check if user is asking for device list
    if any(phrase in transcript.lower() for phrase in ["list devices", "show devices", "what devices", "available devices"]):
        if not has_creds:
            setup_message = f"Please configure your Meross credentials first at: /login?uid={uid}"
            return OMIWebhookResponse(status="success", message=setup_message)
        
        try:
            manager, http_api_client, devices = await get_all_devices(email, password)
            try:
                device_names = [d.name for d in devices if d.online]
                if device_names:
                    device_list = ", ".join(device_names)
                    list_message = f"Your devices: {device_list}"
                else:
                    list_message = "No online devices found in your account."
            finally:
                await cleanup(manager, http_api_client)
            
            return OMIWebhookResponse(status="success", message=list_message)
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            error_msg = "Error connecting to your Meross account. Please check your credentials."
            return OMIWebhookResponse(status="success", message=error_msg)
    
    # Check credentials before processing intent
    if not has_creds:
        # Skip intent inference if credentials are missing
        setup_message = f"Please configure your Meross credentials first. Visit /login?uid={uid}"
        logger.info(f"No credentials configured for uid {uid}, skipping intent processing")
        return OMIWebhookResponse(status="success", message=setup_message)
    
    # Infer intent from transcript (only if credentials are available)
    try:
        intent = infer_intent_from_transcript(transcript)
    except ValueError as err:
        logger.error(f"OpenAI configuration error: {err}")
        error_message = "I'm having trouble understanding your request right now."
        return OMIWebhookResponse(status="success", message=error_message)
    except Exception as err:
        logger.error(f"Intent inference failed: {err}")
        error_message = "I couldn't analyze that request. Please try again."
        return OMIWebhookResponse(status="success", message=error_message)
    
    logger.debug(f"Intent result: {intent}")
    
    # Execute device action if applicable
    response_message = intent.get("assistant_message", "")
    
    if intent.get("action") in {"turn_on", "turn_off"}:
        try:
            # Only use device_uuid from cookie if no device name is specified in intent
            # Otherwise, let perform_device_action find the device by name
            intent_device_name = intent.get("device", "").strip()
            use_cookie_device = device_uuid and not intent_device_name
            
            success, device_message = await perform_device_action(
                intent_device_name if intent_device_name else None,
                intent["action"],
                email,
                password,
                device_uuid if use_cookie_device else None
            )
            if success:
                response_message = device_message
            else:
                response_message = device_message or response_message
        except Exception as err:
            logger.error(f"Error executing device action: {err}")
            response_message = "I had trouble controlling the device. Please check your credentials and try again."
    
    # Add follow-up if present (only after successful processing)
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


@router.get("/devices/{device_uuid}/on", response_model=LightControlResponse)
async def device_on(
    device_uuid: str,
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password")
):
    """Turn on a specific device by UUID. Uses credentials from cookies."""
    if not meross_email or not meross_password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not found. Please log in at /login"
        )
    
    try:
        success, message = await turn_on_device(meross_email, meross_password, device_uuid)
        if success:
            return LightControlResponse(status="success", message=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error turning on device {device_uuid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_uuid}/off", response_model=LightControlResponse)
async def device_off(
    device_uuid: str,
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password")
):
    """Turn off a specific device by UUID. Uses credentials from cookies."""
    if not meross_email or not meross_password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not found. Please log in at /login"
        )
    
    try:
        success, message = await turn_off_device(meross_email, meross_password, device_uuid)
        if success:
            return LightControlResponse(status="success", message=message)
        else:
            raise HTTPException(status_code=500, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error turning off device {device_uuid}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/on", response_model=LightControlResponse)
async def light_on(
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password"),
    meross_device_uuid: Optional[str] = Cookie(None, alias="meross_device_uuid")
):
    """Turn on device. Uses selected device from cookie or first device."""
    if not meross_email or not meross_password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not found. Please log in at /login"
        )
    
    try:
        success, message = await turn_on_device(meross_email, meross_password, meross_device_uuid)
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
async def light_off(
    request: Request,
    meross_email: Optional[str] = Cookie(None, alias="meross_email"),
    meross_password: Optional[str] = Cookie(None, alias="meross_password"),
    meross_device_uuid: Optional[str] = Cookie(None, alias="meross_device_uuid")
):
    """Turn off device. Uses selected device from cookie or first device."""
    if not meross_email or not meross_password:
        raise HTTPException(
            status_code=401,
            detail="Meross credentials not found. Please log in at /login"
        )
    
    try:
        success, message = await turn_off_device(meross_email, meross_password, meross_device_uuid)
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
    
    # Get credentials from cookies
    has_creds = bool(meross_email and meross_password)
    
    if intent.get("action") in {"turn_on", "turn_off"} and has_creds:
        try:
            success, device_message = await perform_device_action(
                intent.get("device", ""), intent["action"], meross_email, meross_password
            )
            action_result["executed"] = success
            action_result["message"] = device_message
        except Exception as err:
            logger.error(f"Error executing device action: {err}")
            action_result["message"] = "Device action failed."
    elif intent.get("action") in {"turn_on", "turn_off"} and not has_creds:
        action_result["message"] = "Meross credentials missing. Please log in at /login"

    return VoiceCommandResponse(
        status="success",
        transcript=transcript,
        intent=intent,
        deviceAction=action_result,
        audioFilePath=str(saved_path) if saved_path else None,
    )


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - redirects to login or devices page based on authentication."""
    meross_email = request.cookies.get("meross_email")
    meross_password = request.cookies.get("meross_password")
    has_creds = credentials_configured(meross_email, meross_password)
    
    if has_creds:
        # User is logged in, redirect to device selection
        return RedirectResponse(url="/devices", status_code=302)
    else:
        # User not logged in, redirect to login
        return RedirectResponse(url="/login", status_code=302)


@router.get("/status")
async def status(request: Request):
    """Get service status"""
    meross_email = request.cookies.get("meross_email")
    meross_password = request.cookies.get("meross_password")
    has_creds = credentials_configured(meross_email, meross_password)
    
    return {
        "active": True,
        "uptime": time.time() - start_time,
        "credentials_configured": has_creds
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
