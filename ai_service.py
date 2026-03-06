from openai import OpenAI
from schemas import WorkoutPlan, NutritionPlan

client = OpenAI()

def generate_workout_from_ai(user_data: dict, user_goal: str) -> WorkoutPlan:
    ai_context = f"""
    You are MetronPro, an elite AI fitness coach.
    USER PROFILE: Age {user_data.get('age')}, Weight {user_data.get('weight_kg')}kg, Height {user_data.get('height_cm')}cm.
    Supplements: {', '.join(user_data.get('supplements', []))}. Cardio: {user_data.get('cardio_routine', 'None')}.
    USER GOAL: {user_goal}
    Design a 1-day workout plan perfectly tailored to this profile. Use 'coach_note' to explain the choices.
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_context}],
        response_format=WorkoutPlan,
        max_tokens=800,
        temperature=0.7
    )
    return completion.choices[0].message.parsed

def generate_nutrition_from_ai(user_data: dict, diet_goal: str) -> NutritionPlan:
    """Generates a hyper-personalized nutrition plan based on user physiological state."""
    ai_context = f"""
    You are MetronPro, an elite AI sports nutritionist.
    USER PROFILE: Age {user_data.get('age')}, Weight {user_data.get('weight_kg')}kg, Height {user_data.get('height_cm')}cm.
    Supplements: {', '.join(user_data.get('supplements', []))}. Cardio: {user_data.get('cardio_routine', 'None')}.
    DIET GOAL: {diet_goal}
    
    INSTRUCTIONS:
    Design a highly effective 1-day meal plan. 
    1. Calculate exact daily calories and macros (Protein, Carbs, Fats) appropriate for their weight and goal.
    2. Divide these into specific meals with realistic ingredients.
    3. Use the 'coach_note' to provide guidance on exactly when they should take their listed supplements.
    """
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": ai_context}],
        response_format=NutritionPlan,
        max_tokens=1200,
        temperature=0.7
    )
    return completion.choices[0].message.parsed