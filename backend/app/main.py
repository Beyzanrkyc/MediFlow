from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes import triage
from app.routes import chat   # ✅ ADD THIS

# Initialize app
app = FastAPI(
    title="MediFlow AI",
    description="AI-powered NHS Triage & Healthcare Optimization Platform",
    version="1.0.0"
)

# CORS (so frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(triage.router, prefix="/triage", tags=["Triage"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])  # ✅ ADD THIS

# Root endpoint (health check)
@app.get("/")
def root():
    return {
        "message": "MediFlow AI is running 🚀",
        "status": "ok"
    }

# Optional: health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }