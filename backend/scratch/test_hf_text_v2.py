import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HUGGINGFACE_API_KEY")
if not api_key:
    print("HUGGINGFACE_API_KEY not found in .env")
    exit(1)

def query_hf(model_id, text):
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": text}
    response = requests.post(api_url, headers=headers, json=payload)
    print(f"Model: {model_id} | Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response Text: {response.text}")
        return None
    return response.json()

models = [
    "PirateXX/AI-Content-Detector",
    "desklib/ai-text-detector-v1.01",
    "Joshfcooper/ai-text-detector-optimized"
]

test_text = "It is important to note that artificial intelligence has revolutionized numerous industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities in pattern recognition."

for model in models:
    print(f"\nTesting model: {model}")
    try:
        result = query_hf(model, test_text)
        if result:
            print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
