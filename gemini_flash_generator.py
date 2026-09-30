from google import genai
from .config import GOOGLE_API_KEY, GEMINI_NUTRITION_MODEL

def generate_nutrition_tip_with_flash(goal: str, age: int) -> tuple[str, str]:
    if not GOOGLE_API_KEY:
        return _fallback_tip(goal, age), "local fallback"

    prompt = f"""
Give one concise, practical nutrition or recovery tip for a person with the general fitness goal:
{goal}
Age: {age}

Return plain text only, maximum 80 words.
Avoid calorie targets, restrictive dieting, supplements, or medical claims.
For minors, emphasize regular balanced meals, hydration, sleep, and guidance from a parent/guardian or qualified professional.
"""
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_NUTRITION_MODEL,
            contents=prompt,
        )
        return response.text.strip(), "Gemini"
    except Exception:
        return _fallback_tip(goal, age), "local fallback (Gemini unavailable)"

def _fallback_tip(goal: str, age: int) -> str:
    if goal == "muscle gain":
        tip = "Include a balanced meal with a protein source, vegetables or fruit, and a carbohydrate source, and stay hydrated."
    elif goal == "weight loss":
        tip = "Focus on regular balanced meals with vegetables or fruit, protein, whole grains, and water rather than restrictive dieting."
    elif goal == "flexibility":
        tip = "Support recovery with regular balanced meals, enough fluids, and consistent sleep."
    else:
        tip = "Aim for regular balanced meals, enough water, and consistent sleep to support everyday energy and recovery."
    if age < 18:
        tip += " If you are under 18, involve a parent/guardian or qualified health professional for individualized nutrition advice."
    return tip
