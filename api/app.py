import asyncio
import io
import json
import os
from typing import Dict, Optional, Tuple
from flask import Flask, jsonify, render_template, request, redirect, url_for
import logging
from dotenv import load_dotenv
load_dotenv()
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = os.environ.get("MEROSS_EMAIL")
PASSWORD = os.environ.get("MEROSS_PASSWORD")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

_openai_client: Optional[OpenAI] = None

app = Flask(__name__)


def credentials_configured():
    """Return True when Meross credentials are ready to use."""
    return bool(EMAIL and PASSWORD)


def get_openai_client() -> OpenAI:
    """Initialise and return a reusable OpenAI client."""
    global _openai_client

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured. Set it before using voice commands.")

    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)

    return _openai_client

async def get_device():
    """Get the device for each request"""
    if not credentials_configured():
        raise Exception("Meross credentials not configured. Visit /login to set them.")

    http_api_client = await MerossHttpClient.async_from_user_password(
        email=EMAIL, password=PASSWORD, api_base_url="https://iot.meross.com")
    
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss110")
    
    if len(plugs) < 1:
        raise Exception("No mss110 plugs found")
    
    device = plugs[0]
    await device.async_update()
    
    return manager, http_api_client, device

async def cleanup(manager, http_api_client):
    """Clean up connections"""
    manager.close()
    await http_api_client.async_logout()

def run_async(coro):
    """Helper to run async code"""
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

async def turn_on_light():
    """Turn on the light"""
    manager, http_api_client, device = await get_device()
    try:
        await device.async_turn_on(channel=0)
        return True, f"Turned on {device.name}"
    finally:
        await cleanup(manager, http_api_client)

async def turn_off_light():
    """Turn off the light"""
    manager, http_api_client, device = await get_device()
    try:
        await device.async_turn_off(channel=0)
        return True, f"Turned off {device.name}"
    finally:
        await cleanup(manager, http_api_client)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Collect Meross credentials from the user."""
    global EMAIL, PASSWORD

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        password = (request.form.get('password') or '').strip()

        if not email or not password:
            return render_template('login.html', error="Email and password are required.", email=email)

        EMAIL = email
        PASSWORD = password
        logger.debug("Meross credentials set via login page for email %s", EMAIL)
        logger.info("Meross credentials configured via login page.")
        return redirect(url_for('home'))

    if credentials_configured():
        return redirect(url_for('home'))

    return render_template('login.html', error=None, email=EMAIL or '')


def transcribe_audio_file(file_storage) -> str:
    """Run Whisper transcription on uploaded audio."""
    client = get_openai_client()

    audio_bytes = file_storage.read()
    if not audio_bytes:
        raise ValueError("Audio file is empty.")

    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = file_storage.filename or "omi-audio.wav"
    audio_stream.seek(0)

    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_stream,
        response_format="text"
    )

    return transcription.strip()


INTENT_PROMPT = (
    "You are Omi, a helpful smart-home assistant. "
    "Given a user's speech transcript, decide if they want to control the coffee machine or room light. "
    "Respond with strict JSON containing: action ('turn_on', 'turn_off', or 'none'), device ('coffee machine', 'room light', or ''), "
    "assistant_message (what you will say back to the user), and follow_up (any short suggestion or question). "
    "Infer intent even if indirect (e.g., tired -> coffee machine on, too dark -> room light on). "
    "If unsure, set action to 'none' and ask a clarifying question."
)


def infer_intent_from_transcript(transcript: str) -> Dict[str, str]:
    """Use GPT to convert transcript into a structured intent."""
    client = get_openai_client()
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [{"type": "text", "text": INTENT_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": transcript}],
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
        }
    )

    try:
        payload = json.loads(response.output_text)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse intent JSON: %s", exc)
        raise ValueError("Intent parsing failed") from exc

    return payload


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
    for keyword, canonical in DEVICE_KEYWORDS.items():
        if keyword in name:
            return canonical
    return None


def perform_device_action(device_name: str, action: str) -> Tuple[bool, str]:
    """Execute the requested Meross action if supported."""
    canonical = resolve_device_name(device_name)
    if canonical is None:
        return False, f"I don't recognise the device '{device_name}'."

    if action == "turn_on":
        success, message = run_async(turn_on_light())
    elif action == "turn_off":
        success, message = run_async(turn_off_light())
    else:
        return False, "No action executed."

    if canonical == "coffee machine" and success:
        return True, "Coffee machine powered on."

    if canonical == "room light" and action == "turn_on" and success:
        return True, "Room light switched on."

    if canonical == "room light" and action == "turn_off" and success:
        return True, "Room light switched off."

    return success, message

@app.route('/on', methods=['GET'])
def light_on():
    """Turn light on"""
    if not credentials_configured():
        return jsonify({"status": "error", "message": "Please log in at /login to configure Meross credentials."}), 401

    try:
        success, message = run_async(turn_on_light())
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        logger.error(f"Error turning on light: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/off', methods=['GET'])
def light_off():
    """Turn light off"""
    if not credentials_configured():
        return jsonify({"status": "error", "message": "Please log in at /login to configure Meross credentials."}), 401

    try:
        success, message = run_async(turn_off_light())
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        logger.error(f"Error turning off light: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/voice', methods=['POST'])
def handle_voice_command():
    """Process voice input: transcribe, infer intent, execute device action."""
    if 'audio' not in request.files:
        return jsonify({"status": "error", "message": "Upload audio as form-data with field 'audio'."}), 400

    audio_file = request.files['audio']

    try:
        transcript = transcribe_audio_file(audio_file)
    except RuntimeError as err:
        logger.error("Voice command failed, configuration missing: %s", err)
        return jsonify({"status": "error", "message": str(err)}), 500
    except Exception as err:
        logger.error("Unable to transcribe audio: %s", err)
        return jsonify({"status": "error", "message": "Transcription failed."}), 500

    try:
        intent = infer_intent_from_transcript(transcript)
    except RuntimeError as err:
        logger.error("OpenAI configuration error: %s", err)
        return jsonify({"status": "error", "message": str(err)}), 500
    except Exception as err:
        logger.error("Intent inference failed: %s", err)
        return jsonify({"status": "error", "message": "Intent analysis failed."}), 500

    action_result: Dict[str, Optional[str]] = {
        "executed": False,
        "device": intent.get("device"),
        "message": None,
    }

    if intent.get("action") in {"turn_on", "turn_off"} and credentials_configured():
        try:
            success, device_message = perform_device_action(intent.get("device", ""), intent["action"])
            action_result["executed"] = success
            action_result["message"] = device_message
        except Exception as err:
            logger.error("Error executing device action: %s", err)
            action_result["message"] = "Device action failed."
    elif intent.get("action") in {"turn_on", "turn_off"} and not credentials_configured():
        action_result["message"] = "Meross credentials missing. Configure them at /login."

    return jsonify({
        "status": "success",
        "transcript": transcript,
        "intent": intent,
        "deviceAction": action_result,
    }), 200

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    if not credentials_configured():
        return redirect(url_for('login'))

    return jsonify({
        "message": "Simple Light Controller",
        "endpoints": {
            "GET /on": "Turn light on",
            "GET /off": "Turn light off",
            "POST /voice": "Transcribe audio and control devices"
        },
        "credentialsConfigured": credentials_configured()
    }), 200

if __name__ == '__main__':
    if not credentials_configured():
        logger.warning("MEROSS_EMAIL and MEROSS_PASSWORD not set; visit /login to configure them before toggling devices.")
    
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env == 'production':
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
