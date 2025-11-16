"""
Vercel Serverless Function Handler
This file is required for Vercel to properly handle Flask requests
"""

import sys
import os

# Add parent directory to path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import app - this will initialize Flask
try:
    from app import app
    
    # Vercel's @vercel/python builder automatically detects Flask apps
    # Just export the app variable
    handler = app
    
except Exception as e:
    # If import fails, create a minimal error handler
    import traceback
    error_details = traceback.format_exc()
    
    from flask import Flask
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        return f"""
        <h1>Application Error</h1>
        <p>Error loading application:</p>
        <pre>{str(e)}</pre>
        <details>
            <summary>Traceback</summary>
            <pre>{error_details}</pre>
        </details>
        """, 500
    
    handler = error_app

