from fastapi import APIRouter, HTTPException
from .schemas import ChatRequest, ChatResponse, HealthCheckResponse, ErrorResponse
from .service import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

@router.post("/chat",
            response_model=ChatResponse,
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"}
            })
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Chat with AI fitness coach for personalized advice and support.
    
    **Features:**
    - **Retrieval-Augmented Generation (RAG)**: Uses fitness knowledge base
    - **Groq API**: Powered by Llama 3.1 8B model
    - **Fitness Expertise**: Specialized in workout, nutrition, and wellness advice
    - **Motivational Support**: Encouraging and practical responses
    
    **Topics Covered:**
    - Workout programming and exercise techniques
    - Nutrition and meal planning
    - Weight management strategies
    - Muscle building and strength training
    - Cardiovascular fitness
    - Recovery and injury prevention
    - Motivation and habit formation
    
    **Example Questions:**
    - "What's the best way to lose belly fat?"
    - "How much protein should I eat for muscle gain?"
    - "Can you suggest a workout routine for beginners?"
    - "How do I stay motivated to exercise?"
    
    **Parameters:**
    - **query**: Your fitness or nutrition question (1-500 characters)
    - **user_id**: Optional user identifier for tracking
    - **conversation_id**: Optional conversation ID for context
    
    **Returns:**
    - Personalized fitness advice from AI coach
    - Response timestamp
    - Conversation ID for follow-up questions
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get response from chatbot service
        response_text = await chatbot_service.get_chat_response(request.query)
        
        return ChatResponse(
            success=True,
            response=response_text,
            conversation_id=request.conversation_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chatbot service error: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Check the health status of the chatbot service.
    
    Verifies that Groq API is configured and embedding model is loaded.
    """
    try:
        health_status = chatbot_service.check_service_health()
        
        status = "healthy" if health_status["service_ready"] else "unhealthy"
        message = "Chatbot service is ready" if health_status["service_ready"] else "Chatbot service has configuration issues"
        
        return HealthCheckResponse(
            status=status,
            service="chatbot",
            message=message,
            groq_api_configured=health_status["groq_api_configured"],
            embedder_loaded=health_status["embedder_loaded"]
        )
    
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service="chatbot",
            message=f"Health check failed: {str(e)}",
            groq_api_configured=False,
            embedder_loaded=False
        )

@router.get("/info")
async def get_chatbot_info():
    """
    Get information about the chatbot service capabilities.
    """
    return {
        "service_name": "FitAI Coach",
        "description": "AI-powered fitness and nutrition chatbot",
        "model": "Llama 3.1 8B (via Groq)",
        "capabilities": [
            "Workout programming",
            "Exercise technique guidance",
            "Nutrition advice",
            "Meal planning tips",
            "Weight management strategies",
            "Muscle building guidance",
            "Cardiovascular fitness",
            "Recovery recommendations",
            "Motivation and support"
        ],
        "features": [
            "Retrieval-Augmented Generation (RAG)",
            "Fitness knowledge base",
            "Context-aware responses",
            "Motivational coaching style"
        ],
        "limitations": [
            "Not a replacement for medical advice",
            "Cannot diagnose medical conditions",
            "Recommends consulting professionals for serious concerns"
        ],
        "knowledge_base_topics": 15
    }

@router.get("/examples")
async def get_example_queries():
    """
    Get example queries to help users understand chatbot capabilities.
    """
    return {
        "beginner_questions": [
            "How do I start working out as a complete beginner?",
            "What exercises can I do at home without equipment?",
            "How many days per week should I exercise?"
        ],
        "nutrition_questions": [
            "What should I eat before a workout?",
            "How much protein do I need daily?",
            "Can you suggest healthy meal ideas for weight loss?"
        ],
        "advanced_questions": [
            "How do I break through a strength plateau?",
            "What's the best way to structure a push-pull-legs routine?",
            "How should I adjust my diet during a cutting phase?"
        ],
        "motivation_questions": [
            "How do I stay consistent with my workouts?",
            "I'm feeling demotivated, any tips?",
            "How do I build healthy fitness habits?"
        ],
        "recovery_questions": [
            "How important are rest days?",
            "What should I do for muscle soreness?",
            "How much sleep do I need for optimal recovery?"
        ]
    }
