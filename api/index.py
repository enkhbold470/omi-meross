"""
Vercel serverless entry point for FastAPI app
According to Vercel docs: https://vercel.com/docs/frameworks/backend/fastapi
FastAPI is supported natively - just export the 'app' instance directly.
"""
import sys
from pathlib import Path

# Ensure the api directory is in the Python path for Vercel serverless
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

# Add both current and parent directories to path
for directory in [current_dir, parent_dir]:
    directory_str = str(directory)
    if directory_str not in sys.path:
        sys.path.insert(0, directory_str)

# Import and export the FastAPI app instance directly
# Vercel's native FastAPI support expects 'app' variable, not 'handler'
from app import app

