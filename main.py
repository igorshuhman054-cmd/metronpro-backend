from fastapi import FastAPI, HTTPException, Depends
from database import supabase
from schemas import UserProfile, WorkoutPlan, NutritionPlan
from ai_service import generate_workout_from_ai, generate_nutrition_from_ai
from security import verify_api_key

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
    try:
        profile_res = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        if not profile_res.data: raise HTTPException(status_code=404, detail="User profile not found.")
        return generate_workout_from_ai(profile_res.data[0], user_goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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