"""
Vercel Serverless Function Handler
This file is required for Vercel to properly handle Flask requests
"""

from app import app

# Export the Flask app - Vercel will handle it automatically
# The @vercel/python builder expects the app to be exported

