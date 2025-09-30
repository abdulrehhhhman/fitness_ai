from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all module routers
from backend.recommender.routes import router as recommender_router
from backend.vision.routes import router as vision_router
# from backend.predictive.routes import predictive_router # <--- REMOVED
from backend.chatbot.routes import router as chatbot_router

# Create FastAPI instance
app = FastAPI(
    title="Family Care Fitness AI API",
    # EDITED: Updated description to remove 'predictive analytics'
    description="A comprehensive AI-powered fitness and health platform with personalized recommendations, computer vision analysis, and AI coaching chatbot",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(recommender_router)
app.include_router(vision_router)
# app.include_router(predictive_router) # <--- REMOVED
app.include_router(chatbot_router)

@app.get("/")
async def root():
    """
    Root endpoint - API welcome message with complete feature overview
    """
    return {
        "message": "Welcome to Family Care Fitness AI API",
        "version": "4.0.0",
        "description": "Complete fitness and health management platform with AI coaching",
        "features": {
            "recommender": [
                "Personalized fitness and nutrition recommendations",
                "Calorie calculation based on goals and activity",
                "Meal planning with dietary preferences and allergies",
                "Workout suggestions tailored to fitness goals"
            ],
            "vision": [
                "Computer vision exercise form analysis via video upload",
                "Automatic repetition counting for 4 exercise types",
                "Real-time form feedback and quality scoring",
                "Support for squats, push-ups, lunges, and planks"
            ],
            # REMOVED: "predictive" block
            "chatbot": [
                "AI-powered fitness coach for personalized advice",
                "Natural language conversation interface",
                "RAG-based knowledge retrieval for accurate responses",
                "Motivational support and guidance"
            ]
        },
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "modules": {
                "recommender": "/recommender",
                "vision": "/vision",
                # REMOVED: "predictive": "/predictive",
                "chatbot": "/chatbot"
            }
        },
        "key_capabilities": [
            "🎯 Smart Recommendations",
            "👁️ AI Vision Analysis",
            # REMOVED: "📈 Predictive Analytics",
            "💬 AI Fitness Coach",
            "🏥 Health Monitoring",
            "📱 RESTful API Design"
        ]
    }

@app.get("/health")
async def health_check():
    """
    Comprehensive health check for all services
    """
    health_status = {
        "status": "healthy",
        "message": "Family Care Fitness AI API is running",
        "version": "4.0.0",
        "services": {
            "recommender": "healthy",
            # REMOVED: "predictive": "healthy"
        }
    }
    
    # Check vision service health
    try:
        from backend.vision.service import vision_service
        vision_health = vision_service.check_service_health()
        
        health_status["services"]["vision"] = "healthy" if vision_health["service_ready"] else "degraded"
        health_status["vision_components"] = {
            "mediapipe": vision_health["mediapipe_available"],
            "opencv": vision_health["opencv_available"]
        }
    except Exception as e:
        health_status["services"]["vision"] = "error"
        health_status["vision_error"] = str(e)
    
    # Check chatbot service health
    try:
        from backend.chatbot.service import chatbot_service
        chatbot_health = chatbot_service.check_service_health()
        
        health_status["services"]["chatbot"] = "healthy" if chatbot_health["service_ready"] else "degraded"
        health_status["chatbot_components"] = {
            "groq_api": chatbot_health["groq_api_configured"],
            "embedder": chatbot_health["embedder_loaded"]
        }
    except Exception as e:
        health_status["services"]["chatbot"] = "error"
        health_status["chatbot_error"] = str(e)
    
    # Overall status determination
    service_statuses = list(health_status["services"].values())
    if "error" in service_statuses:
        health_status["status"] = "degraded"
        health_status["message"] = "API is running but some services have errors"
    elif "degraded" in service_statuses:
        health_status["status"] = "degraded"
        health_status["message"] = "API is running but some services are degraded"
    
    return health_status

@app.get("/modules")
async def get_modules_info():
    """
    Get detailed information about all available modules
    """
    return {
        "total_modules": 3, # EDITED: 4 -> 3
        "modules": {
            "recommender": {
                "name": "Fitness & Nutrition Recommender",
                "description": "Personalized recommendations based on user profile",
                "endpoints": [
                    "POST /recommender/recommendations",
                    "GET /recommender/health",
                    "GET /recommender/info"
                ],
                "key_features": [
                    "BMR/TDEE calculation",
                    "Goal-based calorie adjustment",
                    "Diet preference filtering",
                    "Allergy-aware meal selection"
                ]
            },
            "vision": {
                "name": "Computer Vision Exercise Analysis",
                "description": "AI-powered exercise form analysis and rep counting",
                "endpoints": [
                    "POST /vision/analyze-video",
                    "GET /vision/health",
                    "GET /vision/info",
                    "GET /vision/exercises/{type}/info"
                ],
                "key_features": [
                    "Pose detection with MediaPipe",
                    "Exercise form analysis",
                    "Automatic repetition counting",
                    "Real-time feedback generation"
                ],
                "supported_exercises": ["squats", "pushups", "lunges", "planks"]
            },
            # REMOVED: "predictive" block
            "chatbot": {
                "name": "AI Fitness Coach Chatbot",
                "description": "Conversational AI for fitness advice and motivation",
                "endpoints": [
                    "POST /chatbot/chat",
                    "GET /chatbot/health",
                    "GET /chatbot/info",
                    "GET /chatbot/examples"
                ],
                "key_features": [
                    "Natural language understanding",
                    "RAG-based knowledge retrieval",
                    "Fitness expertise (Llama 3.1 8B)",
                    "Motivational coaching style"
                ],
                "capabilities": [
                    "Workout programming",
                    "Nutrition guidance",
                    "Exercise techniques",
                    "Motivation support"
                ]
            }
        },
        "integration_benefits": [
            "Complete fitness ecosystem in one API",
            "Cross-module data compatibility",
            "Comprehensive health monitoring",
            "AI-powered personalization",
            "Scalable microservice architecture"
        ]
    }

@app.get("/stats")
async def get_api_stats():
    """
    Get API statistics and capabilities summary
    """
    # Total Endpoints: 3 (recommender) + 4 (vision) + 4 (chatbot) + 3 (system: /, /health, /stats) = 14
    return {
        "api_version": "4.0.0",
        "total_endpoints": 14, # EDITED: 20 -> 14
        "endpoint_breakdown": {
            "recommender": 3,
            "vision": 4,
            # REMOVED: "predictive": 6,
            "chatbot": 4,
            "system": 3 # EDITED: 2 -> 3 for /, /health, /stats (and /modules if it's considered system)
        },
        "supported_features": {
            "exercise_types": 4,
            "diet_preferences": 4,
            "activity_levels": 5,
            # REMOVED: "prediction_timeframes": 3,
            "health_risk_categories": 4,
            "chatbot_topics": 15
        },
        "technical_stack": [
            "FastAPI",
            "Pydantic",
            "MediaPipe",
            "OpenCV",
            "NumPy",
            "Groq API",
            "Sentence Transformers",
            "FAISS"
        ],
        "ai_models": [
            "MediaPipe Pose Detection",
            "Llama 3.1 8B (Groq)",
            "all-MiniLM-L6-v2 (Embeddings)"
        ],
        "data_processing": {
            "real_time_analysis": True,
            "batch_processing": True,
            "file_upload_support": True,
            "form_validation": True,
            "conversational_ai": True,
            "rag_enabled": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug
    )
