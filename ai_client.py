# ai_client.py
import os, time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load GEMINI_API_KEY from .env
load_dotenv() 

def call_ai(filename, content):
    """
    If USE_MOCK=1, returns gold_fixes. Otherwise, calls the Gemini API.
    """
    # --- MOCK/OFFLINE MODE ---
    if os.getenv("USE_MOCK","1") == "1":
        p = os.path.join("gold_fixes", filename)
        if os.path.exists(p):
            print("Using mock fix from gold_fixes.")
            return open(p,"r").read()
        raise RuntimeError("Mock mode enabled, but gold_fix not found.")

    # --- GEMINI API CALL MODE ---
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")
    
    client = genai.Client(api_key=api_key)
    
    # Strict prompt template (Ensures reproducible output)
    prompt_template = (
        "You are a code-fixing assistant. Task: fix the bug in this Python module so that "
        "all existing unit tests pass. Constraints: return ONLY the corrected full file "
        "content inside a single fenced python code block. Do not write any explanation "
        "or commentary.\n\n"
        f"File: {filename}\n"
        f"-----CODE-----\n"
        f"{content}\n"
        f"-----END-----\n"
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_template,
        config=types.GenerateContentConfig(
            temperature=0.0
        )
    )

    text = response.text.strip()
    
    # Extract code block
    if text.startswith("```python"):
        text = text.replace("```python", "", 1)
        if text.endswith("```"):
            text = text[:-3]
    
    if not text:
        raise RuntimeError("AI returned an empty response.")
        
    return text.strip()