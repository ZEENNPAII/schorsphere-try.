"""
Vercel Serverless Function Handler
This file is required for Vercel to properly handle Flask requests
"""

import sys
import os
import traceback

# Add parent directory to path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Try to import and initialize the app
try:
    # Import app - this will initialize Flask
    from app import app
    
    # Vercel's @vercel/python builder automatically detects Flask apps
    # The app variable is exported and Vercel will use it
    
except Exception as e:
    # If import fails, create a minimal error handler that shows the error
    from flask import Flask, jsonify
    
    error_app = Flask(__name__)
    error_traceback = traceback.format_exc()
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            'error': 'Application failed to load',
            'message': str(e),
            'traceback': error_traceback,
            'path': path
        }), 500
    
    app = error_app

# Export app for Vercel
# Vercel will automatically detect Flask apps
