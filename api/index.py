"""
Vercel serverless entry point for FastAPI app
"""
import sys
import os
from pathlib import Path

# Ensure the api directory is in the Python path for Vercel serverless
# In Vercel, files are deployed to /var/task/api/
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent.resolve()

# Add both current and parent directories to path
for directory in [current_dir, parent_dir]:
    directory_str = str(directory)
    if directory_str not in sys.path:
        sys.path.insert(0, directory_str)

# Now import app from the same directory
from app import app

# This is the handler that Vercel expects
handler = app

