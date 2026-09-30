from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .config import BASE_DIR, ADMIN_KEY
from .schemas import UserInput, FeedbackRequest
from .database import (
    save_user, save_plan, get_user, get_latest_plan,
    update_plan, get_all_users_with_plans, delete_user
)
from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .updated_plan import update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None},
    )

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    name: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(
            name=name, user_id=user_id, age=age, weight=weight,
            goal=goal, intensity=intensity
        )
        user = save_user(data.model_dump())
        workout_plan, workout_source = generate_workout_gemini(
            data.name, data.age, data.weight, data.goal, data.intensity
        )
        nutrition_tip, nutrition_source = generate_nutrition_tip_with_flash(
            data.goal, data.age
        )
        plan = save_plan(user.id, workout_plan, nutrition_tip)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "workout_source": workout_source,
                "nutrition_source": nutrition_source,
                "message": None,
                "error": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": f"Please check your input. {exc}"},
            status_code=400,
        )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        request_data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(request_data.user_id)
        plan = get_latest_plan(request_data.user_id)

        if not user or not plan:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={"error": "User ID was not found. Generate a plan first."},
                status_code=404,
            )

        revised_plan, source = update_workout_plan(
            plan.original_plan,
            request_data.feedback,
            user.goal,
            user.age,
        )
        updated = update_plan(plan.id, revised_plan, request_data.feedback)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": updated,
                "workout_plan": revised_plan,
                "nutrition_tip": plan.nutrition_tip,
                "workout_source": source,
                "nutrition_source": "stored tip",
                "message": "Your feedback was saved and the plan was updated.",
                "error": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": f"Feedback could not be processed: {exc}"},
            status_code=400,
        )

def _admin_allowed(admin_key: str | None) -> bool:
    return not ADMIN_KEY or admin_key == ADMIN_KEY

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, admin_key: str | None = None):
    if not _admin_allowed(admin_key):
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={"users": [], "error": "Invalid admin key.", "admin_key": ""},
            status_code=403,
        )
    records = get_all_users_with_plans()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"records": records, "admin_key": admin_key or "", "error": None},
    )

@router.post("/delete-user")
def remove_user(user_id: str = Form(...), admin_key: str = Form("")):
    if not _admin_allowed(admin_key):
        return HTMLResponse("Invalid admin key.", status_code=403)
    delete_user(user_id)
    return RedirectResponse(
        url=f"/view-all-users?admin_key={admin_key}",
        status_code=303,
    )
