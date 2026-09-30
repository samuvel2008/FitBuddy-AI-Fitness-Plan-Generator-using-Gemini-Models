from google import genai
from .config import GOOGLE_API_KEY, GEMINI_WORKOUT_MODEL

def update_workout_plan(original_plan: str, feedback: str, goal: str, age: int) -> tuple[str, str]:
    if not GOOGLE_API_KEY:
        return _fallback_update(original_plan, feedback), "local fallback"

    prompt = f"""
You are FitBuddy. Revise the existing general educational workout plan below using the user's feedback.

Goal: {goal}
Age: {age}
Feedback: {feedback}

Existing plan:
{original_plan}

Return a clear 7-day plan in plain text.
Keep the plan conservative and practical.
Do not provide medical diagnosis, extreme exercise, extreme dieting, supplements, or unsafe instructions.
If the feedback requests something unsafe, replace it with a safer alternative.
For minors, keep recommendations conservative and mention parent/guardian or qualified professional guidance where appropriate.
"""
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_WORKOUT_MODEL,
            contents=prompt,
        )
        return response.text.strip(), "Gemini"
    except Exception:
        return _fallback_update(original_plan, feedback), "local fallback (Gemini unavailable)"

def _fallback_update(original_plan: str, feedback: str) -> str:
    return f"""{original_plan}

UPDATED VERSION
Feedback received: {feedback}

Adjustment note:
The local test mode keeps the existing plan and records the requested feedback. When a Gemini API key is configured, the AI will regenerate the plan using the feedback.
"""
