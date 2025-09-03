from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.recommender.routes import router as recommender_router
from backend.vision.routes import router as vision_router

# Create FastAPI instance
app = FastAPI(
    title="Family Care Fitness AI API",
    description="An AI-powered fitness and nutrition recommendation system with computer vision exercise analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommender_router)
app.include_router(vision_router)

@app.get("/")
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "Welcome to Family Care Fitness AI API",
        "version": "2.0.0",
        "features": [
            "Personalized fitness and nutrition recommendations",
            "Computer vision exercise form analysis via video upload",
            "Automatic repetition counting",
            "Form feedback and quality scoring"
        ],
        "docs": "/docs",
        "health": "/health",
        "modules": {
            "recommender": "/recommender",
            "vision": "/vision"
        }
    }

@app.get("/health")
async def health_check():
    """
    Global health check endpoint
    """
    try:
        # Import here to avoid circular imports
        from backend.vision.service import vision_service
        
        # Check vision service health
        vision_health = vision_service.check_service_health()
        
        return {
            "status": "healthy",
            "message": "Family Care Fitness AI API is running",
            "services": {
                "recommender": "healthy",
                "vision": "healthy" if vision_health["service_ready"] else "degraded"
            },
            "vision_components": {
                "mediapipe": vision_health["mediapipe_available"],
                "opencv": vision_health["opencv_available"]
            }
        }
    except Exception as e:
        return {
            "status": "degraded", 
            "message": "API is running but some services may be unavailable",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)