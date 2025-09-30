from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User's fitness-related question")
    user_id: Optional[str] = Field(None, description="Optional user ID for conversation tracking")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

class ChatResponse(BaseModel):
    success: bool = Field(default=True, description="Request success status")
    response: str = Field(..., description="Chatbot's response")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Response timestamp")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for tracking")

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    message: str = Field(..., description="Status message")
    groq_api_configured: bool = Field(..., description="Whether Groq API key is configured")
    embedder_loaded: bool = Field(..., description="Whether embedding model is loaded")

class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")