import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Checking Available Models ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # We want the string after 'models/'
            model_id = m.name.split('/')[-1]
            print(f"Available Model ID: {model_id}")
except Exception as e:
    print(f"Connection Error: {e}")