import json
from google import genai

from .config import GOOGLE_API_KEY, GEMINI_WORKOUT_MODEL

def _client():
    if not GOOGLE_API_KEY:
        return None
    return genai.Client(api_key=GOOGLE_API_KEY)

def _safe_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()
    return json.loads(text)

def _fallback_plan(name: str, goal: str, intensity: str) -> str:
    level = {
        "low": "easy, comfortable effort",
        "medium": "moderate effort",
        "high": "challenging but controlled effort",
    }[intensity]
    return f"""FITBUDDY 7-DAY PLAN
Name: {name}
Goal: {goal.title()}
Intensity: {intensity.title()}

Day 1 - Full Body
Warm-up: 5-10 minutes of easy movement.
Main workout: Squats 2 x 10, wall/incline push-ups 2 x 8, glute bridges 2 x 10, easy walking 10 minutes.
Cooldown: Gentle stretching.
Effort: {level}.

Day 2 - Cardio & Mobility
Warm-up: 5 minutes.
Main workout: Brisk walk or similar low-impact cardio for 20 minutes; mobility exercises for 5-10 minutes.
Cooldown: Gentle stretching.

Day 3 - Recovery
Light walking and comfortable mobility only.
Focus on hydration, sleep, and recovery.

Day 4 - Full Body
Warm-up: 5-10 minutes.
Main workout: Sit-to-stand 2 x 10, incline push-ups 2 x 8, step-ups 2 x 8 each side, light core exercise 2 x 10.
Cooldown: Gentle stretching.

Day 5 - Cardio
Warm-up: 5 minutes.
Main workout: Comfortable cardio for 20-25 minutes.
Cooldown: Gentle stretching.

Day 6 - Mobility & Core
Warm-up: 5 minutes.
Main workout: Mobility flow 10 minutes plus comfortable core exercises.
Cooldown: Breathing and stretching.

Day 7 - Rest / Active Recovery
Easy movement only if comfortable. Review how you felt during the week.

Safety note: This is a general educational plan, not medical advice. Stop any exercise that causes pain or unusual symptoms and ask a qualified adult/health professional for individualized guidance."""

def generate_workout_gemini(name: str, age: int, weight: float, goal: str, intensity: str) -> tuple[str, str]:
    client = _client()
    if client is None:
        return _fallback_plan(name, goal, intensity), "local fallback"

    prompt = f"""
You are FitBuddy, a cautious fitness-planning assistant.
Create a general 7-day educational workout plan for:
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Preferred intensity: {intensity}

Return ONLY valid JSON with this shape:
{{
  "title": "string",
  "days": [
    {{
      "day": "Day 1",
      "focus": "string",
      "warmup": "string",
      "workout": ["string"],
      "cooldown": "string"
    }}
  ],
  "safety_note": "string"
}}

Requirements:
- Exactly 7 days.
- Keep exercise instructions simple and non-graphic.
- Include rest/recovery.
- Do not prescribe supplements, extreme dieting, or dangerous exercises.
- For minors, keep recommendations conservative and encourage involving a parent/guardian or qualified professional.
- Do not diagnose or treat medical conditions.
- Do not claim the plan is medically personalized.
"""
    try:
        response = client.models.generate_content(
            model=GEMINI_WORKOUT_MODEL,
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        data = _safe_json(response.text)
        lines = [data.get("title", "FITBUDDY 7-DAY PLAN"), ""]
        for day in data.get("days", []):
            lines.append(f'{day.get("day", "Day")} - {day.get("focus", "")}')
            lines.append(f'Warm-up: {day.get("warmup", "")}')
            for item in day.get("workout", []):
                lines.append(f"- {item}")
            lines.append(f'Cooldown/Recovery: {day.get("cooldown", "")}')
            lines.append("")
        lines.append(f"Safety note: {data.get('safety_note', 'Use this as general educational guidance.')}")
        return "\n".join(lines), "Gemini"
    except Exception:
        return _fallback_plan(name, goal, intensity), "local fallback (Gemini unavailable)"
