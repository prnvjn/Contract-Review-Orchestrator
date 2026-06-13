import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

api_key = os.environ.get("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ Error: ANTHROPIC_API_KEY not found in .env file.")
else:
    print(f"🔑 Using API Key: {api_key[:10]}...")
    try:
        client = Anthropic(api_key=api_key)
        
        print("📡 Fetching available models...")
        page = client.models.list()
        
        print("✅ Models found:")
        for model in page.data:
            print(f" - {model.id}")
            
    except Exception as e:
        print(f"❌ Failed to connect to Anthropic: {e}")
