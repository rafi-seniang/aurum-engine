import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .core.config import settings
from .api.routes import router as api_router
from .services.bot_engine import bot_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start quant trading engine
    await bot_engine.start()
    yield
    # Shutdown
    bot_engine.is_running = False

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Check if built frontend exists, mount static files
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If file exists in dist (like manifest.json, favicon, etc.), serve it
        possible_file = os.path.join(frontend_dist, full_path)
        if os.path.isfile(possible_file):
            return FileResponse(possible_file)
        # Otherwise fallback to index.html for SPA routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def index():
        return {
            "name": settings.app_name,
            "status": "online",
            "api_docs": "/docs",
            "message": "Backend engine is running. Frontend dist not yet built."
        }
