# src/tests/conftest.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env to get the Gemini API key
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=dotenv_path)