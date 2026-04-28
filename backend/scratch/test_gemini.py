import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

# List models to see available ones
try:
    print("Available models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")

# Try a simple generation with gemini-2.0-flash-exp
model_name = 'gemini-2.0-flash-exp'
print(f"\nTesting generation with {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, are you working?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error with {model_name}: {e}")

# Try with gemini-1.5-flash as well
model_name = 'gemini-1.5-flash'
print(f"\nTesting generation with {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Hello, are you working?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error with {model_name}: {e}")
