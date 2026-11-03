import os
import json
from dotenv import load_dotenv
from groq import Groq, APIError
from pydantic import BaseModel, ValidationError

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Change model names HERE only. Primary first, fallback second.
MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
MAX_RETRIES = 2  # attempts per model


def _call(messages: list[dict], model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def _extract_json(text: str) -> dict:
    """LLMs often wrap JSON in text or ``` fences. Grab from first { to last }."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in the reply")
    return json.loads(text[start:end + 1])


def ask_text(system: str, user: str) -> str:
    """Plain text answer, with fallback to the next model if one fails."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    for model in MODELS:
        try:
            return _call(messages, model)
        except APIError as e:
            print(f"[llm] {model} failed: {e}. Trying next model...")
    raise RuntimeError("All models failed")


def ask_json(system: str, user: str, schema: type[BaseModel]) -> BaseModel:
    """Ask for JSON, validate it against `schema`, retry with the error
    message if invalid, and fall back to the next model if retries run out."""
    for model in MODELS:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        for attempt in range(1, MAX_RETRIES + 1):
            raw = ""
            try:
                raw = _call(messages, model)
                return schema.model_validate(_extract_json(raw))
            except (ValueError, ValidationError) as e:
                # ValueError covers bad JSON; ValidationError covers wrong shape
                print(f"[llm] {model} attempt {attempt} invalid: {str(e)[:150]}")
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": f"Your reply was invalid: {e}\nReturn ONLY the corrected JSON object.",
                })
            except APIError as e:
                print(f"[llm] {model} API error: {e}")
                break  # no point retrying a broken model, go to fallback
        print(f"[llm] Switching away from {model}")
    raise RuntimeError("All models and retries failed")