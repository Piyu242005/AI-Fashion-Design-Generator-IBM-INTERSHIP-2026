# Streamlit Cloud deployment configuration
# Place this file at: frontend/streamlit_app.py (entry point for Streamlit Cloud)
# Or configure in Streamlit Cloud dashboard to point to frontend/app.py

# Required secrets in Streamlit Cloud dashboard (Settings → Secrets):
# API_BASE_URL = "https://your-render-app.onrender.com"

# This file serves as the Streamlit Cloud entry point
# It simply imports and runs the main app

import sys
import os

# Add frontend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the main app
from app import *  # noqa: F401, F403
