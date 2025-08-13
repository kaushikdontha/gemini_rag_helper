import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models:")
try:
    models = genai.list_models()
    for m in models:
        print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
