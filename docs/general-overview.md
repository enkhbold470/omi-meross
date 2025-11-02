 Overview

  - Repository is a minimalist Flask service built to toggle a Meross smart plug, with all runtime logic living in api/app.py:19-114.
  - Startup loads .env variables via python-dotenv and configures app-wide logging at INFO level (api/app.py:5-17).

  Request Flow

  - /on and /off routes wrap async coroutines with run_async so synchronous Flask handlers can drive the Meross SDK (api/app.py:43-91).
  - Each request creates a fresh Meross HTTP client and manager, performs device discovery restricted to mss110 plugs, updates the first device, invokes the on/off command, and then logs out (api/app.py:19-71).
  - cleanup always runs via finally to close the manager and session (api/app.py:38-42).

  Environment & Deployment

  - Requires MEROSS_EMAIL and MEROSS_PASSWORD to be present (optionally from .env) before anything will work; missing values abort startup in CLI mode (api/app.py:14-16, api/app.py:104-108).
  - Development uses Flask’s built-in server while production switches to Waitress when FLASK_ENV=production (api/app.py:109-114).
  - Vercel routing sends all traffic to the Python entry point, enabling serverless-style deployment (vercel.json:3-5).
  - Dependencies include Flask, meross-iot, python-dotenv, and waitress; extra MQTT libraries are listed but not directly referenced in the current code (requirements.txt:1-7).

  Risks / Follow-Ups

  - Per-request discovery/login is simple but adds latency and repeated authentication; consider caching the manager/device or adding connection pooling.
  - Only the first mss110 device is ever addressed; multi-device environments may need selection logic.
  - The module-level EMAIL/PASSWORD values are captured once at import; hot reloads or credential rotation would require restarting the process.
  - Unused packages in requirements.txt could be pruned unless needed transitively.

  If you want next steps:

  1. Add integration tests or a dry-run mode that mocks Meross to exercise on/off flows.
  2. Introduce device selection/config and reuse of the Meross manager to reduce discovery overhead.
