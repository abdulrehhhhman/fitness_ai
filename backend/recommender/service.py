
from typing import List, Dict, Any
import random

class RecommenderService:
    def __init__(self):
        # Sample workout data categorized by goal
        self.workouts = {
            "weight_loss": [
                "Jogging (30 min)",
                "High-Intensity Interval Training (HIIT)",
                "Cycling (45 min)",
                "Swimming (30 min)",
                "Burpees (3 sets of 10)",
                "Jump Rope (20 min)",
                "Mountain Climbers (3 sets of 15)"
            ],
            "muscle_gain": [
                "Bench Press (3 sets of 8-10)",
                "Squats (3 sets of 8-10)",
                "Deadlifts (3 sets of 6-8)",
                "Pull-ups (3 sets of 6-10)",
                "Overhead Press (3 sets of 8-10)",
                "Barbell Rows (3 sets of 8-10)",
                "Dips (3 sets of 8-12)"
            ],
            "maintenance": [
                "Push-ups (3 sets of 12)",
                "Bodyweight Squats (3 sets of 15)",
                "Planks (3 sets of 60 sec)",
                "Lunges (3 sets of 12 each leg)",
                "Light Jogging (25 min)",
                "Yoga (30 min)",
                "Resistance Band Exercises"
            ]
        }
        
        # Sample meal data categorized by diet preference
        self.meals = {
            "veg": [
                "Vegetable Stir-fry with Brown Rice",
                "Chickpea Salad Bowl",
                "Quinoa and Black Bean Bowl",
                "Greek Yogurt with Berries",
                "Avocado Toast with Eggs",
                "Lentil Curry with Rice",
                "Spinach and Cheese Omelet",
                "Vegetable Soup with Whole Grain Bread"
            ],
            "non_veg": [
                "Grilled Chicken Breast with Vegetables",
                "Salmon with Sweet Potato",
                "Turkey and Vegetable Wrap",
                "Egg White Scramble with Spinach",
                "Lean Beef Stir-fry",
                "Tuna Salad with Mixed Greens",
                "Chicken Caesar Salad",
                "Fish Tacos with Cabbage Slaw"
            ],
            "vegan": [
                "Tofu Curry with Brown Rice",
                "Quinoa Buddha Bowl",
                "Chickpea and Vegetable Curry",
                "Almond Butter Toast with Banana",
                "Lentil and Vegetable Soup",
                "Vegan Protein Smoothie Bowl",
                "Black Bean and Sweet Potato Bowl",
                "Chia Seed Pudding with Fruits"
            ],
            "none": [
                "Mixed Green Salad",
                "Oatmeal with Fruits",
                "Vegetable Soup",
                "Fruit Smoothie",
                "Rice and Vegetables",
                "Pasta with Marinara Sauce",
                "Baked Sweet Potato",
                "Greek Salad"
            ]
        }
    
    def calculate_bmr(self, age: int, gender: str, weight: float, height: float) -> float:
        """
        Calculate Basal Metabolic Rate using Harris-Benedict Equation (Revised)
        """
        if gender.lower() == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:  # female
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure based on activity level
        """
        activity_multipliers = {
            "sedentary": 1.2,     # Little to no exercise
            "light": 1.375,       # Light exercise 1-3 days/week
            "moderate": 1.55,     # Moderate exercise 3-5 days/week
            "active": 1.725       # Heavy exercise 6-7 days/week
        }
        
        multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
        return bmr * multiplier
    
    def adjust_calories_for_goal(self, tdee: float, goal: str) -> int:
        """
        Adjust TDEE based on fitness goal
        """
        goal_adjustments = {
            "weight_loss": -500,
            "muscle_gain": 500,
            "maintenance": 0
        }
        
        adjustment = goal_adjustments.get(goal.lower(), 0)
        return int(tdee + adjustment)
    
    def filter_meals_by_allergies(self, meals: List[str], allergies: List[str]) -> List[str]:
        """
        Filter out meals that contain allergens
        """
        if not allergies:
            return meals
        
        # Simple allergen filtering (in a real app, you'd have more detailed ingredient data)
        allergen_keywords = {
            "nuts": ["almond", "peanut", "walnut", "cashew"],
            "dairy": ["cheese", "yogurt", "milk"],
            "gluten": ["bread", "pasta", "wheat"],
            "eggs": ["egg", "omelet"],
            "soy": ["tofu", "soy"],
            "fish": ["salmon", "tuna", "fish"],
            "shellfish": ["shrimp", "crab", "lobster"]
        }
        
        filtered_meals = []
        for meal in meals:
            meal_lower = meal.lower()
            contains_allergen = False
            
            for allergy in allergies:
                allergy_lower = allergy.lower()
                # Check if allergy is in our keyword mapping
                if allergy_lower in allergen_keywords:
                    keywords = allergen_keywords[allergy_lower]
                    if any(keyword in meal_lower for keyword in keywords):
                        contains_allergen = True
                        break
                # Direct keyword match
                elif allergy_lower in meal_lower:
                    contains_allergen = True
                    break
            
            if not contains_allergen:
                filtered_meals.append(meal)
        
        return filtered_meals
    
    def select_workouts(self, goal: str, count: int = 4) -> List[str]:
        """
        Select appropriate workouts based on goal
        """
        available_workouts = self.workouts.get(goal.lower(), self.workouts["maintenance"])
        
        # Return random selection of workouts (up to the requested count)
        selected_count = min(count, len(available_workouts))
        return random.sample(available_workouts, selected_count)
    
    def select_meals(self, diet_preference: str, allergies: List[str], count: int = 5) -> List[str]:
        """
        Select appropriate meals based on diet preference and allergies
        """
        available_meals = self.meals.get(diet_preference.lower(), self.meals["none"])
        
        # Filter out meals with allergens
        filtered_meals = self.filter_meals_by_allergies(available_meals, allergies or [])
        
        if not filtered_meals:
            # Fallback to basic meals if all meals are filtered out
            filtered_meals = self.meals["none"]
            filtered_meals = self.filter_meals_by_allergies(filtered_meals, allergies or [])
        
        # Return random selection of meals (up to the requested count)
        selected_count = min(count, len(filtered_meals))
        return random.sample(filtered_meals, selected_count) if filtered_meals else []
    
    def generate_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function to generate complete fitness recommendations
        """
        # Extract user data
        age = user_data["age"]
        gender = user_data["gender"]
        weight = user_data["weight"]
        height = user_data["height"]
        goal = user_data["goal"]
        activity_level = user_data["activity_level"]
        diet_preference = user_data["diet_preference"]
        allergies = user_data.get("allergies", [])
        
        # Calculate calorie target
        bmr = self.calculate_bmr(age, gender, weight, height)
        tdee = self.calculate_tdee(bmr, activity_level)
        calorie_target = self.adjust_calories_for_goal(tdee, goal)
        
        # Select workouts and meals
        workouts = self.select_workouts(goal)
        meals = self.select_meals(diet_preference, allergies)
        
        return {
            "calorie_target": calorie_target,
            "workouts": workouts,
            "meals": meals,
            "bmr": round(bmr, 1),
            "tdee": round(tdee, 1)
        }


# Create a singleton instance
recommender_service = RecommenderService()