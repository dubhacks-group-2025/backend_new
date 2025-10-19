from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routes.tasks import router as tasks_router

app = FastAPI(title="Image Generation API", version="1.0.0")

# Mount the images directory
images_path = Path(__file__).parent.parent / 'images'
app.mount("/images", StaticFiles(directory=str(images_path)), name="images")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

@app.get("/")
async def root():
    return {"message": "Image Generation API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
