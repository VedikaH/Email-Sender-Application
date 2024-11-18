
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the base directory of your project
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = os.path.join(BASE_DIR, '.env')

print(f"Looking for .env file at: {ENV_FILE}")
print(f"File exists: {os.path.exists(ENV_FILE)}")

# Load environment variables from .env file
load_dotenv(ENV_FILE)

class Settings:
    PROJECT_NAME: str = "Email Sender"
    VERSION: str = "1.0.0"
    
    # Required environment variables
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME")
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")

# Global settings instance
settings = Settings()

# For debugging purposes
def print_settings():
    print("\nCurrent Settings:")
    for field in [field for field in dir(settings) if not field.startswith('_')]:
        # Don't print sensitive information
        if 'secret' in field.lower() or 'password' in field.lower() or 'key' in field.lower():
            value = '***HIDDEN***'
        else:
            value = getattr(settings, field)
        print(f"{field}: {value}")