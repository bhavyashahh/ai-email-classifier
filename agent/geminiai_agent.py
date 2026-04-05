import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

def get_action(state):
    response = client.models.generate_content(
        model= 'gemini-2.5-flash',
        contents = state,
        config=types.GenerateContentConfig(
            system_instruction = "You are a spam classifier"
        )
    )

    return response.text.strip()
