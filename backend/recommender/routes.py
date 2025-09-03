
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from .service import recommender_service

# Create router instance
router = APIRouter(prefix="/recommender", tags=["Recommender"])

# Pydantic models for request validation
class UserInputModel(BaseModel):
    age: int = Field(..., ge=13, le=100, description="User's age in years")
    gender: str = Field(..., description="User's gender")
    weight: float = Field(..., gt=0, le=500, description="User's weight in kg")
    height: float = Field(..., gt=0, le=300, description="User's height in cm")
    goal: str = Field(..., description="Fitness goal")
    activity_level: str = Field(..., description="Activity level")
    diet_preference: str = Field(..., description="Dietary preference")
    allergies: Optional[List[str]] = Field(default=[], description="List of allergies")
    
    # Validators
    @validator('gender')
    def validate_gender(cls, v):
        allowed_genders = ['male', 'female']
        if v.lower() not in allowed_genders:
            raise ValueError(f'Gender must be one of: {", ".join(allowed_genders)}')
        return v.lower()
    
    @validator('goal')
    def validate_goal(cls, v):
        allowed_goals = ['weight_loss', 'muscle_gain', 'maintenance']
        if v.lower() not in allowed_goals:
            raise ValueError(f'Goal must be one of: {", ".join(allowed_goals)}')
        return v.lower()
    
    @validator('activity_level')
    def validate_activity_level(cls, v):
        allowed_levels = ['sedentary', 'light', 'moderate', 'active']
        if v.lower() not in allowed_levels:
            raise ValueError(f'Activity level must be one of: {", ".join(allowed_levels)}')
        return v.lower()
    
    @validator('diet_preference')
    def validate_diet_preference(cls, v):
        allowed_diets = ['veg', 'non_veg', 'vegan', 'none']
        if v.lower() not in allowed_diets:
            raise ValueError(f'Diet preference must be one of: {", ".join(allowed_diets)}')
        return v.lower()
    
    @validator('allergies')
    def validate_allergies(cls, v):
        if v is None:
            return []
        # Convert to lowercase for consistency
        return [allergy.lower().strip() for allergy in v if allergy.strip()]

class RecommendationResponse(BaseModel):
    calorie_target: int = Field(..., description="Daily calorie target")
    workouts: List[str] = Field(..., description="Recommended workouts")
    meals: List[str] = Field(..., description="Recommended meals")
    bmr: Optional[float] = Field(None, description="Basal Metabolic Rate")
    tdee: Optional[float] = Field(None, description="Total Daily Energy Expenditure")
    message: str = Field(default="Recommendations generated successfully")

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

@router.post("/recommendations", 
             response_model=RecommendationResponse,
             responses={
                 400: {"model": ErrorResponse, "description": "Bad Request"},
                 422: {"model": ErrorResponse, "description": "Validation Error"},
                 500: {"model": ErrorResponse, "description": "Internal Server Error"}
             })
async def get_recommendations(user_input: UserInputModel) -> RecommendationResponse:
    """
    Generate personalized fitness and nutrition recommendations based on user input.
    
    This endpoint calculates daily calorie requirements using the Harris-Benedict equation,
    adjusts for fitness goals, and provides tailored workout and meal recommendations.
    
    **Parameters:**
    - **age**: User's age (13-100 years)
    - **gender**: male or female
    - **weight**: Weight in kilograms
    - **height**: Height in centimeters
    - **goal**: weight_loss, muscle_gain, or maintenance
    - **activity_level**: sedentary, light, moderate, or active
    - **diet_preference**: veg, non_veg, vegan, or none
    - **allergies**: Optional list of allergies to avoid in meal recommendations
    
    **Returns:**
    - Daily calorie target
    - Recommended workouts based on goal
    - Recommended meals based on dietary preferences and allergies
    - BMR and TDEE values for reference
    """
    try:
        # Convert Pydantic model to dict
        user_data = user_input.dict()
        
        # Generate recommendations using the service
        recommendations = recommender_service.generate_recommendations(user_data)
        
        # Validate that we have recommendations
        if not recommendations.get("workouts"):
            raise HTTPException(
                status_code=500, 
                detail="Unable to generate workout recommendations"
            )
        
        if not recommendations.get("meals"):
            raise HTTPException(
                status_code=500, 
                detail="Unable to generate meal recommendations. Try adjusting your dietary preferences or allergies."
            )
        
        # Format response
        response = RecommendationResponse(
            calorie_target=recommendations["calorie_target"],
            workouts=recommendations["workouts"],
            meals=recommendations["meals"],
            bmr=recommendations.get("bmr"),
            tdee=recommendations.get("tdee"),
            message="Recommendations generated successfully"
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating recommendations: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the recommender service.
    """
    return {
        "status": "healthy",
        "service": "recommender",
        "message": "Recommender service is running"
    }

@router.get("/info")
async def get_service_info():
    """
    Get information about available options for the recommender service.
    """
    return {
        "supported_genders": ["male", "female"],
        "supported_goals": ["weight_loss", "muscle_gain", "maintenance"],
        "supported_activity_levels": ["sedentary", "light", "moderate", "active"],
        "supported_diet_preferences": ["veg", "non_veg", "vegan", "none"],
        "common_allergies": ["nuts", "dairy", "gluten", "eggs", "soy", "fish", "shellfish"],
        "calorie_adjustments": {
            "weight_loss": "-500 kcal from TDEE",
            "muscle_gain": "+500 kcal from TDEE",
            "maintenance": "No adjustment from TDEE"
        }
    }