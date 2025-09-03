from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum

class ExerciseType(str, Enum):
    SQUATS = "squats"
    PUSHUPS = "pushups" 
    LUNGES = "lunges"
    PLANKS = "planks"

class VideoAnalysisRequest(BaseModel):
    exercise_type: ExerciseType = Field(..., description="Type of exercise to analyze")
    
    class Config:
        use_enum_values = True

class WebcamAnalysisRequest(BaseModel):
    exercise_type: ExerciseType = Field(..., description="Type of exercise to analyze")
    duration_seconds: Optional[int] = Field(default=30, ge=10, le=300, description="Duration for webcam analysis in seconds")
    
    class Config:
        use_enum_values = True

class FormFeedback(BaseModel):
    timestamp: float = Field(..., description="Timestamp in video when feedback applies")
    message: str = Field(..., description="Feedback message about form")
    severity: str = Field(..., description="Severity level: info, warning, error")

class RepetitionData(BaseModel):
    rep_number: int = Field(..., description="Repetition number")
    timestamp: float = Field(..., description="Timestamp when rep was completed")
    form_quality: float = Field(..., ge=0, le=1, description="Form quality score (0-1)")
    feedback: List[str] = Field(default=[], description="Feedback for this repetition")

class PlankData(BaseModel):
    start_time: float = Field(..., description="When plank position was achieved")
    end_time: Optional[float] = Field(None, description="When plank position was lost")
    duration: float = Field(..., description="Duration in seconds")
    form_quality: float = Field(..., ge=0, le=1, description="Average form quality")
    feedback: List[str] = Field(default=[], description="Form feedback during plank")

class PoseKeypoint(BaseModel):
    x: float = Field(..., description="X coordinate (normalized 0-1)")
    y: float = Field(..., description="Y coordinate (normalized 0-1)")
    z: Optional[float] = Field(None, description="Z coordinate (depth)")
    visibility: float = Field(..., ge=0, le=1, description="Visibility score")

class FrameAnalysis(BaseModel):
    frame_number: int = Field(..., description="Frame number in video")
    timestamp: float = Field(..., description="Timestamp in seconds")
    pose_detected: bool = Field(..., description="Whether pose was detected in frame")
    key_angles: Dict[str, float] = Field(default={}, description="Key angles for the exercise")
    form_score: float = Field(..., ge=0, le=1, description="Form score for this frame")
    in_position: bool = Field(..., description="Whether person is in correct exercise position")

class ExerciseAnalysisResult(BaseModel):
    exercise_type: str = Field(..., description="Type of exercise analyzed")
    total_frames: int = Field(..., description="Total frames processed")
    frames_with_pose: int = Field(..., description="Frames where pose was detected")
    analysis_duration: float = Field(..., description="Total analysis time in seconds")
    
    # Exercise-specific results
    total_reps: Optional[int] = Field(None, description="Total repetitions counted (not for planks)")
    plank_duration: Optional[float] = Field(None, description="Total plank duration in seconds")
    
    # Detailed data
    repetitions: List[RepetitionData] = Field(default=[], description="Detailed repetition data")
    plank_sessions: List[PlankData] = Field(default=[], description="Plank session data")
    
    # Overall feedback
    average_form_score: float = Field(..., ge=0, le=1, description="Average form quality score")
    overall_feedback: List[str] = Field(default=[], description="Overall exercise feedback")
    form_feedback: List[FormFeedback] = Field(default=[], description="Timestamped form feedback")
    
    # Performance metrics
    best_rep_quality: Optional[float] = Field(None, description="Best repetition quality score")
    consistency_score: Optional[float] = Field(None, description="Consistency across reps")
    
class AnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether analysis was successful")
    message: str = Field(..., description="Status message")
    result: Optional[ExerciseAnalysisResult] = Field(None, description="Analysis results")
    processing_time: float = Field(..., description="Total processing time in seconds")

class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    message: str = Field(..., description="Status message")
    mediapipe_available: bool = Field(..., description="Whether MediaPipe is available")
    opencv_available: bool = Field(..., description="Whether OpenCV is available")

class ServiceInfoResponse(BaseModel):
    supported_exercises: List[str] = Field(..., description="List of supported exercises")
    supported_formats: List[str] = Field(..., description="Supported video formats")
    max_video_duration: int = Field(..., description="Maximum video duration in seconds")
    max_file_size: int = Field(..., description="Maximum file size in MB")
    pose_detection_model: str = Field(..., description="Pose detection model used")