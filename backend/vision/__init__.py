
"""
Vision Module

This module provides computer vision capabilities for fitness exercise analysis.
It uses MediaPipe and OpenCV to detect poses, count repetitions, and analyze form.

Supported exercises:
- Squats: Rep counting and knee/hip angle analysis
- Push-ups: Rep counting and body alignment analysis  
- Lunges: Rep counting and knee positioning analysis
- Planks: Duration tracking and body alignment analysis
"""

from .service import vision_service
from .routes import router
from .schema import ExerciseType, AnalysisResponse, ExerciseAnalysisResult

__all__ = [
    "vision_service", 
    "router", 
    "ExerciseType", 
    "AnalysisResponse", 
    "ExerciseAnalysisResult"
]