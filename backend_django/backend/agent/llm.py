import json
from django.conf import settings
from google import genai
from google.genai import types

from .prompt import SYSTEM_PROMPT

client = genai.Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"


def run_llm(user_message, conversation_context=None):
    """
    Returns STRICT JSON:
    { action, params } OR { message }
    """

    prompt = (
        SYSTEM_PROMPT
        + "\n\nUser message:\n"
        + user_message
        + "\n\nContext:\n"
        + json.dumps(conversation_context or {})
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        text = response.text.strip()
        return json.loads(text)

    except Exception as e:
        return {
            "message": f"LLM error: {str(e)}"
        }
