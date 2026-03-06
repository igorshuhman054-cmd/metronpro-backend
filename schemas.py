from pydantic import BaseModel, Field
from typing import List, Optional

# --- USER PROFILE ---
class UserProfile(BaseModel):
    user_id: str = Field(description="Unique identifier for the user")
    full_name: str = Field(description="User's full name")
    age: int = Field(description="User's age in years")
    weight_kg: float = Field(description="User's weight in kilograms")
    height_cm: int = Field(description="User's height in centimeters")
    supplements: List[str] = Field(default=[], description="List of supplements currently taken")
    cardio_routine: Optional[str] = Field(default=None, description="Details of weekly cardio activities")

# --- WORKOUT MODELS ---
class Exercise(BaseModel):
    name: str = Field(description="Name of the exercise")
    sets: int = Field(description="Number of sets to perform")
    reps: str = Field(description="Repetition range")
    rest_seconds: int = Field(description="Rest time between sets in seconds")
    coach_note: Optional[str] = Field(default=None, description="Specific AI advice tailored to the user")

class WorkoutPlan(BaseModel):
    workout_name: str = Field(description="A catchy name for the workout")
    estimated_time_minutes: int = Field(description="Estimated duration in minutes")
    exercises: List[Exercise] = Field(description="List of exercises in the plan")

# --- NUTRITION MODELS (NEW) ---
class Meal(BaseModel):
    meal_name: str = Field(description="Name of the meal (e.g., Breakfast, Post-Workout)")
    calories: int = Field(description="Total calories for this meal")
    protein_g: int = Field(description="Grams of protein")
    carbs_g: int = Field(description="Grams of carbohydrates")
    fats_g: int = Field(description="Grams of fats")
    ingredients: List[str] = Field(description="List of specific foods and quantities to eat")

class MacroSplit(BaseModel):
    protein_g: int
    carbs_g: int
    fats_g: int

class NutritionPlan(BaseModel):
    daily_calories: int = Field(description="Target daily caloric intake")
    macros: MacroSplit = Field(description="Overall daily macronutrient split")
    meals: List[Meal] = Field(description="Detailed list of meals for the day")
    coach_note: Optional[str] = Field(default=None, description="Specific dietary advice (e.g., timing of supplements like protein powder)")