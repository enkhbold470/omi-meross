import asyncio
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
import logging
from dotenv import load_dotenv
load_dotenv()
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMAIL = os.environ.get("MEROSS_EMAIL")
PASSWORD = os.environ.get("MEROSS_PASSWORD")

app = Flask(__name__)


def credentials_configured():
    """Return True when Meross credentials are ready to use."""
    return bool(EMAIL and PASSWORD)

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

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    if not credentials_configured():
        return redirect(url_for('login'))

    return jsonify({
        "message": "Simple Light Controller",
        "endpoints": {
            "GET /on": "Turn light on",
            "GET /off": "Turn light off"
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
