"""
Smart Gallery Backend - Main Application
Production-ready FastAPI application with AI-powered photo analysis.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import init_db
from app.services.ml_service import ml_service
from app.services.vector_service import vector_service
from app.api import photos, clusters, search, categories

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    logger.info("=" * 50)
    logger.info("🚀 Starting Smart Gallery API...")
    logger.info("=" * 50)
    
    # Initialize database
    logger.info("📦 Initializing database...")
    await init_db()
    
    # Initialize ML models
    logger.info("🤖 Loading ML models...")
    await ml_service.initialize()
    
    logger.info("=" * 50)
    logger.info("✅ Smart Gallery API is ready!")
    logger.info(f"📍 Running on http://{settings.host}:{settings.port}")
    logger.info("=" * 50)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Smart Gallery API...")
    
    # Save vector indices
    vector_service.save_all()
    
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# Smart Gallery API

AI-powered photo gallery backend with:

- **🔍 YOLO Object Detection** - Detect 80+ object types in photos
- **👤 Face Recognition** - Detect faces, extract embeddings, automatic clustering
- **🧠 CLIP Semantic Search** - Search photos using natural language
- **👥 People Clustering** - Automatically group photos by person

## Features

- Upload photos with automatic AI analysis
- Search by text description (e.g., "sunset on beach")
- Search by similar image
- Find all photos of a person
- Filter by detected objects
- View gallery statistics

## Models Used

- **YOLO v8x** - State-of-the-art object detection
- **InsightFace buffalo_l** - Face detection and recognition
- **CLIP ViT-L-14** - Vision-language model for semantic search
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(photos.router)
app.include_router(clusters.router)
app.include_router(search.router)
app.include_router(categories.router)


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.app_name}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', system-ui, sans-serif; 
                background: linear-gradient(135deg, #0a0a0b 0%, #1a1a1d 100%);
                color: #fafafa;
                min-height: 100vh;
                padding: 40px;
            }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .header {{ 
                display: flex; 
                align-items: center; 
                gap: 16px; 
                margin-bottom: 32px;
            }}
            .logo {{ 
                width: 64px; 
                height: 64px; 
                background: linear-gradient(135deg, #f97316, #fb923c);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
            }}
            h1 {{ font-size: 2.5rem; font-weight: 700; }}
            .subtitle {{ color: #a1a1aa; margin-top: 4px; }}
            .card {{
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .card h2 {{ 
                color: #f97316; 
                font-size: 1.25rem; 
                margin-bottom: 16px;
            }}
            .endpoints {{ list-style: none; }}
            .endpoints li {{ 
                padding: 12px 16px;
                background: rgba(0,0,0,0.3);
                border-radius: 8px;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .method {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
            }}
            .get {{ background: #22c55e20; color: #22c55e; }}
            .post {{ background: #3b82f620; color: #3b82f6; }}
            .delete {{ background: #ef444420; color: #ef4444; }}
            a {{ color: #f97316; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .features {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }}
            .feature {{
                text-align: center;
                padding: 20px;
                background: rgba(249,115,22,0.1);
                border-radius: 12px;
            }}
            .feature-icon {{ font-size: 32px; margin-bottom: 8px; }}
            .feature-title {{ font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🖼️</div>
                <div>
                    <h1>Smart Gallery API</h1>
                    <p class="subtitle">v{settings.app_version} • AI-Powered Photo Organizer</p>
                </div>
            </div>
            
            <div class="card">
                <h2>🤖 AI Features</h2>
                <div class="features">
                    <div class="feature">
                        <div class="feature-icon">🎯</div>
                        <div class="feature-title">YOLO v8</div>
                        <div class="subtitle">Object Detection</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">👤</div>
                        <div class="feature-title">InsightFace</div>
                        <div class="subtitle">Face Recognition</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">🔍</div>
                        <div class="feature-title">CLIP</div>
                        <div class="subtitle">Semantic Search</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>📚 Endpoints</h2>
                <ul class="endpoints">
                    <li><span class="method post">POST</span> /photos/upload - Upload photos</li>
                    <li><span class="method get">GET</span> /photos - List all photos</li>
                    <li><span class="method get">GET</span> /clusters - List people</li>
                    <li><span class="method get">GET</span> /categories - List object categories</li>
                    <li><span class="method get">GET</span> /search/text?q= - Semantic search</li>
                    <li><span class="method post">POST</span> /search/image - Image similarity search</li>
                    <li><span class="method get">GET</span> /categories/stats - Gallery statistics</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>📖 Documentation</h2>
                <p>
                    <a href="/docs">📄 Interactive API Docs (Swagger)</a><br><br>
                    <a href="/redoc">📘 ReDoc Documentation</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "models": {
            "yolo": ml_service.yolo_model is not None,
            "insightface": ml_service.face_app is not None,
            "clip": ml_service.clip_model is not None,
        }
    }


# Stats endpoint (duplicate for convenience)
@app.get("/stats")
async def get_stats(db=None):
    """Get gallery statistics."""
    from app.core.database import get_db_context
    from app.services.photo_service import photo_service
    
    async with get_db_context() as db:
        return await photo_service.get_stats(db)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc) if settings.debug else None}
    )
