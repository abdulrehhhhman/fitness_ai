
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.recommender.routes import router as recommender_router

# Create FastAPI instance
app = FastAPI(
    title="Fitness AI API",
    description="An AI-powered fitness and nutrition recommendation system",
    version="1.0.0",
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

@app.get("/")
async def root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "Welcome to Fitness AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    Global health check endpoint
    """
    return {
        "status": "healthy",
        "message": "Fitness AI API is running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)