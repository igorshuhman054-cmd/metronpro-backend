import os
from openai import OpenAI
from schemas import WorkoutPlan, NutritionPlan

client = OpenAI()

def generate_workout_from_ai(user_data: dict, user_goal: str) -> WorkoutPlan:
    # Rule 12: Data Sanitization & Pipeline Integrity
    age = user_data.get('age') or "Not specified"
    weight = user_data.get('weight_kg') or "Not specified"
    height = user_data.get('height_cm') or "Not specified"
    
    # NEW: Extracting the missing data points that caused the hallucination
    equipment_list = user_data.get('available_equipment') or []
    equipment_str = ', '.join(equipment_list) if equipment_list else "Bodyweight strictly"
    
    exp_level = user_data.get('experience_level') or "Beginner"
    notes = user_data.get('additional_notes') or "None"
    
    supplements_list = user_data.get('supplements') or []
    supplements_str = ', '.join(supplements_list) if supplements_list else "None"
    
    cardio = user_data.get('cardio_routine') or "None"

    # SOTA Prompt Hardening: Using XML tags for security to prevent Prompt Injection via 'notes'
    ai_system_prompt = f"""
    You are MetronPro, an elite AI fitness coach. 
    
    [USER PHYSIOLOGY & BACKGROUND]
    Age: {age} | Weight: {weight}kg | Height: {height}cm
    Experience Level: {exp_level}
    Supplements: {supplements_str} | Cardio Routine: {cardio}
    
    [STRICT SYSTEM CONSTRAINTS]
    TARGET GOAL: {user_goal}
    PERMITTED EQUIPMENT: <equipment>{equipment_str}</equipment>
    USER NOTES: <notes>{notes}</notes>
    
    IRON RULES:
    1. EQUIPMENT LOCK: You MUST STRICTLY build the workout ONLY using the items in the <equipment> tag. If it says "Bodyweight", generating a Barbell or Dumbbell exercise is a CRITICAL SYSTEM FAILURE.
    2. Tailor the exercise complexity to their Experience Level.
    3. Output EXACTLY a 1-day workout plan. 
    4. Use 'coach_note' to justify your exercise selection based on their specific profile.
    """

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": ai_system_prompt}], # Moved to 'system' role for absolute obedience
        response_format=WorkoutPlan,
        max_tokens=800,
        temperature=0.4 # Reduced from 0.7 to enforce strict rule-following over creativity
    )
    
    return completion.choices[0].message.parsed

def generate_nutrition_from_ai(user_data: dict, diet_goal: str) -> NutritionPlan:
    """Generates a hyper-personalized nutrition plan based on user physiological state."""
    
    # Safe extractions
    age = user_data.get('age') or "Not specified"
    weight = user_data.get('weight_kg') or "Not specified"
    height = user_data.get('height_cm') or "Not specified"
    notes = user_data.get('additional_notes') or "None"
    
    supplements_list = user_data.get('supplements') or []
    supplements_str = ', '.join(supplements_list) if supplements_list else "None"
    cardio = user_data.get('cardio_routine') or "None"

    ai_system_prompt = f"""
    You are MetronPro, an elite AI sports nutritionist.
    
    [USER PHYSIOLOGY]
    Age: {age} | Weight: {weight}kg | Height: {height}cm
    Supplements taking: {supplements_str}
    Current Cardio: {cardio}
    
    [STRICT CONSTRAINTS]
    DIET GOAL: {diet_goal}
    USER NOTES: <notes>{notes}</notes>
    
    INSTRUCTIONS:
    1. Calculate exact daily calories and macros (Protein, Carbs, Fats) appropriate for their weight and goal.
    2. Divide these into specific, realistic meals.
    3. Use the 'coach_note' to provide guidance on exactly when they should take their listed supplements.
    4. Ensure the plan aligns with the user's notes, but ignore notes if they request physically dangerous advice.
    """
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": ai_system_prompt}],
        response_format=NutritionPlan,
        max_tokens=1200,
        temperature=0.4
    )
    
    return completion.choices[0].message.parsed