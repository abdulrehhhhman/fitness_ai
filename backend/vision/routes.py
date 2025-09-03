from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
import tempfile
import os
import time
from typing import Optional
import aiofiles

from .schema import (
    VideoAnalysisRequest, WebcamAnalysisRequest, AnalysisResponse, 
    ErrorResponse, HealthCheckResponse, ServiceInfoResponse,
    ExerciseType
)
from .service import vision_service

# Create router instance
router = APIRouter(prefix="/vision", tags=["Vision Analysis"])

# Supported video formats
SUPPORTED_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_VIDEO_DURATION = 300  # 5 minutes

async def validate_video_file(file: UploadFile) -> str:
    """Validate uploaded video file and return temp path"""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    # Check file size
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    temp_filename = f"upload_{int(time.time())}_{file.filename}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Save uploaded file to temporary location
        async with aiofiles.open(temp_path, 'wb') as temp_file:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            await temp_file.write(content)
        
        return temp_path
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")

@router.post("/analyze-video", 
             response_model=AnalysisResponse,
             responses={
                 400: {"model": ErrorResponse, "description": "Bad Request"},
                 413: {"model": ErrorResponse, "description": "File Too Large"},
                 422: {"model": ErrorResponse, "description": "Validation Error"},
                 500: {"model": ErrorResponse, "description": "Internal Server Error"}
             })
async def analyze_video(
    exercise_type: ExerciseType = Form(..., description="Type of exercise to analyze"),
    file: UploadFile = File(..., description="Video file to analyze")
) -> AnalysisResponse:
    """
    Analyze uploaded video for exercise form and repetition counting.
    
    **Supported Exercises:**
    - **squats**: Counts repetitions and analyzes knee/hip angles
    - **pushups**: Counts repetitions and analyzes elbow angles and body alignment  
    - **lunges**: Counts repetitions and analyzes knee positioning
    - **planks**: Measures time held in correct position and form quality
    
    **Supported Video Formats:** MP4, AVI, MOV, MKV, WMV
    **Maximum File Size:** 100MB
    **Maximum Duration:** 5 minutes
    
    **Returns:**
    - Exercise analysis results including rep counts or plank duration
    - Form quality scores and detailed feedback
    - Timestamped corrections and suggestions
    """
    temp_path = None
    start_time = time.time()
    
    try:
        # Validate and save uploaded file
        temp_path = await validate_video_file(file)
        
        # Analyze video using vision service
        result = vision_service.analyze_video_file(temp_path, exercise_type.value)
        
        processing_time = time.time() - start_time
        
        return AnalysisResponse(
            success=True,
            message="Video analysis completed successfully",
            result=result,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

@router.post("/analyze-webcam",
             response_model=AnalysisResponse,
             responses={
                 400: {"model": ErrorResponse, "description": "Bad Request"},
                 500: {"model": ErrorResponse, "description": "Internal Server Error"}
             })
async def analyze_webcam(request: WebcamAnalysisRequest) -> AnalysisResponse:
    """
    Start webcam analysis for real-time exercise monitoring.
    
    **Note:** This endpoint is designed for local development and testing.
    In production, consider using WebSocket connections for real-time video analysis.
    
    **Parameters:**
    - **exercise_type**: Type of exercise to monitor
    - **duration_seconds**: How long to analyze (10-300 seconds)
    
    **Returns:**
    - Real-time analysis results
    - Form feedback and rep counting
    
    **Limitations:**
    - Requires local webcam access
    - Not suitable for web deployment without additional setup
    """
    try:
        # For now, return a placeholder response as webcam analysis
        # requires additional setup for web deployment
        return AnalysisResponse(
            success=False,
            message="Webcam analysis not implemented for web deployment. Use video upload instead.",
            result=None,
            processing_time=0.0
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webcam analysis failed: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Check the health status of the vision analysis service.
    
    Verifies that MediaPipe and OpenCV are properly installed and functioning.
    """
    try:
        health_status = vision_service.check_service_health()
        
        status = "healthy" if health_status["service_ready"] else "unhealthy"
        message = "Vision service is ready" if health_status["service_ready"] else "Vision service has issues"
        
        return HealthCheckResponse(
            status=status,
            service="vision",
            message=message,
            mediapipe_available=health_status["mediapipe_available"],
            opencv_available=health_status["opencv_available"]
        )
        
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service="vision", 
            message=f"Health check failed: {str(e)}",
            mediapipe_available=False,
            opencv_available=False
        )

@router.get("/info", response_model=ServiceInfoResponse)
async def get_service_info() -> ServiceInfoResponse:
    """
    Get information about the vision analysis service capabilities.
    
    Returns supported exercises, video formats, and service limitations.
    """
    return ServiceInfoResponse(
        supported_exercises=["squats", "pushups", "lunges", "planks"],
        supported_formats=SUPPORTED_FORMATS,
        max_video_duration=MAX_VIDEO_DURATION,
        max_file_size=MAX_FILE_SIZE // (1024 * 1024),  # Convert to MB
        pose_detection_model="MediaPipe Pose"
    )

@router.get("/exercises/{exercise_type}/info")
async def get_exercise_info(exercise_type: ExerciseType):
    """
    Get specific information about an exercise type.
    
    Returns exercise-specific analysis parameters and form guidelines.
    """
    exercise_info = {
        "squats": {
            "description": "Analyzes squat form focusing on knee and hip angles",
            "key_metrics": ["knee_angle", "hip_angle", "back_position"],
            "form_tips": [
                "Keep knees aligned with toes",
                "Maintain straight back",
                "Descend until thighs are parallel to ground",
                "Keep chest up"
            ],
            "common_mistakes": [
                "Knees caving inward",
                "Not squatting deep enough", 
                "Leaning forward excessively"
            ]
        },
        "pushups": {
            "description": "Analyzes push-up form focusing on elbow angles and body alignment",
            "key_metrics": ["elbow_angle", "body_alignment", "head_position"],
            "form_tips": [
                "Keep body in straight line",
                "Lower chest to ground level",
                "Keep elbows at 45-degree angle",
                "Maintain neutral head position"
            ],
            "common_mistakes": [
                "Sagging hips",
                "Partial range of motion",
                "Flaring elbows too wide",
                "Looking up or down"
            ]
        },
        "lunges": {
            "description": "Analyzes lunge form focusing on knee positioning and balance", 
            "key_metrics": ["front_knee_angle", "back_knee_angle", "balance"],
            "form_tips": [
                "Keep front knee over ankle",
                "Lower back knee toward ground",
                "Maintain upright torso",
                "Step back to starting position"
            ],
            "common_mistakes": [
                "Front knee going past toes",
                "Not lowering enough",
                "Leaning forward",
                "Poor balance"
            ]
        },
        "planks": {
            "description": "Measures plank hold time and analyzes body alignment",
            "key_metrics": ["back_alignment", "hip_position", "hold_duration"],
            "form_tips": [
                "Keep body in straight line",
                "Engage core muscles",
                "Maintain neutral spine",
                "Keep head in line with spine"
            ],
            "common_mistakes": [
                "Hips too high or low",
                "Arching back",
                "Looking up",
                "Not engaging core"
            ]
        }
    }
    
    if exercise_type.value not in exercise_info:
        raise HTTPException(status_code=404, detail="Exercise type not found")
    
    return {
        "exercise_type": exercise_type.value,
        **exercise_info[exercise_type.value]
    }