from fastapi import FastAPI, HTTPException, Depends
from database import supabase
from schemas import UserProfile, WorkoutPlan, NutritionPlan
from ai_service import generate_workout_from_ai, generate_nutrition_from_ai
from security import verify_api_key
from telegram_service import send_telegram_alert

app = FastAPI(title="MetronPro AI Backend", version="0.9.0 - Secured API")

@app.get("/")
async def root():
    return {"message": "MetronPro AI Backend is running securely. Public access is limited."}

# Notice the new 'dependencies=[Depends(verify_api_key)]' injected into each route!

@app.post("/api/v1/profiles", response_model=UserProfile, dependencies=[Depends(verify_api_key)])
async def upsert_user_profile(profile: UserProfile):
    try:
        supabase.table("user_profiles").upsert(profile.model_dump()).execute()
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/v1/generate-plan", response_model=WorkoutPlan, dependencies=[Depends(verify_api_key)])
async def generate_personalized_plan(user_id: str, user_goal: str):
    # Step 1: Safely fetch the user profile
    try:
        profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=404, detail="User profile not found. Create a profile first.")
        user_data = profile_res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

    # Step 2: Generate the workout plan via AI
    try:
        validated_plan = generate_workout_from_ai(user_data, user_goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Workout generation failed: {str(e)}")

    # --- TELEGRAM WEBHOOK INJECTION ---
    try:
        alert_msg = (
            f"🚀 *MetronPro System Alert*\n"
            f"✅ *New AI Workout Generated!*\n"
            f"👤 *User ID:* `{user_id}`\n"
            f"🎯 *Goal:* {user_goal}\n"
            f"⚙️ *System Status:* Optimal"
        )
        send_telegram_alert(alert_msg)
    except Exception:
        pass # Zero Trust: Never let a logging failure crash the user's response
    # ----------------------------------
    # Step 3: Rule 12 & 8 (Data Persistence) - Save the JSON artifact to the database
    try:
        supabase.table("workout_plans").insert({
            "user_id": user_id,
            "goal": user_goal,
            "plan_data": validated_plan.model_dump()
        }).execute()
    except Exception as db_error:
        # Non-blocking error: Log it, but still return the plan to the user so they aren't stuck
        print(f"Database Warning: Could not save workout plan - {str(db_error)}")
    
    return validated_plan

@app.post("/api/v1/generate-nutrition", response_model=NutritionPlan, dependencies=[Depends(verify_api_key)])
async def generate_personalized_nutrition(user_id: str, diet_goal: str):
    try:
        profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        if not profile_res.data:
            raise HTTPException(status_code=404, detail="User profile not found. Create a profile first.")
        user_data = profile_res.data[0]
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Database fetch error: {str(e)}")

    try:
        validated_nutrition = generate_nutrition_from_ai(user_data, diet_goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Nutrition generation failed: {str(e)}")

    try:
        supabase.table("nutrition_plans").insert({
            "user_id": user_id,
            "daily_calories": validated_nutrition.daily_calories,
            "macros": validated_nutrition.macros.model_dump(),
            "meals": [meal.model_dump() for meal in validated_nutrition.meals]
        }).execute()
    except Exception as db_error:
        print(f"Database Warning: Could not save nutrition plan - {str(db_error)}")
    
    return validated_nutrition