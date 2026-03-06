import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load sensitive environment variables securely
load_dotenv()

# --- DATABASE SETUP (Supabase) ---
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Critical Error: Supabase credentials missing in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)