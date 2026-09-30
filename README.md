# FitBuddy – AI Fitness Plan Generator

A FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy documentation.

## Features

- User form: name, user ID, age, weight, goal, intensity
- 7-day workout-plan generation
- Nutrition/recovery tip generation
- Feedback-based plan update
- SQLite persistence with SQLAlchemy
- Admin dashboard
- FastAPI Swagger docs at `/docs`
- Gemini integration through Google's current `google-genai` SDK
- Local fallback mode when no Gemini API key is configured

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── routes.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   └── updated_plan.py
├── templates/
│   ├── index.html
│   ├── result.html
│   ├── all_users.html
│   └── admin.html
├── static/
│   └── style.css
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup – Windows

Open the `FitBuddy` folder in VS Code.

### 1. Create a virtual environment

```powershell
py -m venv venv
```

### 2. Activate it

```powershell
venv\Scripts\activate
```

If PowerShell blocks activation, use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### 3. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env`.

For a no-key local test, leave:

```env
GOOGLE_API_KEY=
```

The app will still generate a safe sample plan using local fallback logic.

For Gemini:

```env
GOOGLE_API_KEY=your_key_here
GEMINI_WORKOUT_MODEL=gemini-2.5-flash
GEMINI_NUTRITION_MODEL=gemini-2.5-flash
```

Use model IDs that are actually available to your Gemini API account.

### 5. Run

```powershell
uvicorn app.main:app --reload
```

Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin: http://127.0.0.1:8000/view-all-users

## Testing

### Test 1 – Home page

Open `/` and verify the form appears.

### Test 2 – Generate without API key

Submit:
- Name: Test User
- User ID: FB001
- Age: 18
- Weight: 60
- Goal: General wellness
- Intensity: Medium

A 7-day local fallback plan should appear. This proves the FastAPI, Jinja2, validation, and SQLite layers work.

### Test 3 – Database

After generating a plan, the file `fitbuddy.db` is created automatically.

Open `/view-all-users` to verify the stored user and plan.

### Test 4 – Feedback

On the result page enter feedback such as:

```text
Please add more recovery time.
```

Submit it. The updated plan/feedback should be stored.

### Test 5 – Gemini

Put a valid Gemini API key in `.env`, restart Uvicorn, and generate another plan. The result page shows `Gemini` as the source when the API call succeeds.

## API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | User form |
| POST | `/generate-workout` | Generate and save a plan |
| POST | `/submit-feedback` | Update a plan |
| GET | `/view-all-users` | Admin dashboard |
| POST | `/delete-user` | Delete a user |
| GET | `/docs` | Swagger UI |

## Notes

The supplied documentation describes Gemini 1.5 Pro and Gemini Flash. The implementation keeps the same architecture and separates workout generation, nutrition generation, and feedback updating, but makes model IDs configurable because Gemini model availability can change.

Do not commit `.env` or API keys to Git.

For real deployment, add proper authentication/authorization to the admin dashboard, HTTPS, rate limiting, and stronger privacy controls.
