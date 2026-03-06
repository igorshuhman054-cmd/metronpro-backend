import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

# Define the name of the header we expect the client to send
API_KEY_NAME = "X-API-Key"

# Load our secret key from the environment
VALID_API_KEY = os.getenv("METRON_API_KEY")

if not VALID_API_KEY:
    raise RuntimeError("CRITICAL ERROR: METRON_API_KEY is missing from the .env file")

# This sets up the security scheme for Swagger UI
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency function to validate the API key in the request header.
    """
    if not api_key or api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Access Denied.",
        )
    return api_key