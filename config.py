"""
Configuration module for the SEO Analysis ADK Project.
Loads environment variables from .env file.
"""

import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# Google API Key for Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    logger.warning(
        "GOOGLE_API_KEY not found in environment variables. "
        "Make sure to set it in your .env file or environment."
    )

# Optional: Google Custom Search Engine credentials
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'seo_analysis.db')

# Request timeout settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

# Agent configuration
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
