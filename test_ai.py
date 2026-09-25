import os
from dotenv import load_dotenv
from google import genai

# Load key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Connect to Gemini
client = genai.Client(api_key=api_key)

print("Connecting to Gemini...")

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="In two short sentences, why is acclimatization essential when trekking above 3,000 meters in Nepal?",
)

print("\n--- Response from Gemini ---")
print(response.text)