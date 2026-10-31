import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for model in ["gemini-3.5-flash-lite", "gemini-3.5-flash"]:
    try:
        r = client.models.generate_content(
            model=model,
            contents="मेरी उम्र 45 साल है। इसे अंग्रेज़ी में एक वाक्य में बताओ।",
        )
        print(model, "OK ->", r.text)
    except Exception as e:
        print(model, "FAILED ->", str(e)[:300])