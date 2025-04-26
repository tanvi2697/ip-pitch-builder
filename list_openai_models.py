import openai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(override=True)

# Set API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# List available models
try:
    models = openai.models.list()
    for model in models.data:
        print(f"✅ {model.id}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
