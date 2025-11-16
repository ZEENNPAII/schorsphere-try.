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
from app import app

# Vercel's @vercel/python builder automatically detects Flask apps
# The app variable is exported and Vercel will use it

