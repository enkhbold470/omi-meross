import asyncio
import os
from flask import Flask, jsonify
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

async def get_device():
    """Get the device for each request"""
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

@app.route('/on', methods=['GET'])
def light_on():
    """Turn light on"""
    try:
        success, message = run_async(turn_on_light())
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        logger.error(f"Error turning on light: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/off', methods=['GET'])
def light_off():
    """Turn light off"""
    try:
        success, message = run_async(turn_off_light())
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e:
        logger.error(f"Error turning off light: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return jsonify({
        "message": "Simple Light Controller",
        "endpoints": {
            "GET /on": "Turn light on",
            "GET /off": "Turn light off"
        }
    }), 200

if __name__ == '__main__':
    if not EMAIL or not PASSWORD:
        logger.error("Please set MEROSS_EMAIL and MEROSS_PASSWORD environment variables")
        exit(1)
    
    flask_env = os.environ.get('FLASK_ENV', 'development')
    if flask_env == 'production':
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
