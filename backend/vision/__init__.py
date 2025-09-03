"""
Vision Module

This module provides computer vision capabilities for fitness exercise analysis
through video upload. It uses MediaPipe and OpenCV to detect poses, count repetitions, 
and analyze form.

Supported exercises:
- Squats: Rep counting and knee/hip angle analysis
- Push-ups: Rep counting and body alignment analysis  
- Lunges: Rep counting and knee positioning analysis
- Planks: Duration tracking and body alignment analysis

Features:
- Video file upload and processing
- Automatic repetition counting
- Form quality scoring (0-1 scale)
- Timestamped feedback and corrections
- Exercise-specific analysis parameters
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