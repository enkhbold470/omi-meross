"""
Vercel serverless entry point for FastAPI app
"""
from app import app

# This is the handler that Vercel expects
handler = app

