from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import api_router
from app.db.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="RazorBuy — AI Agentic Commerce Platform FastAPI Server"
)

# Set up CORS
# NOTE: allow_origins="*" + allow_credentials=True is invalid per the CORS spec
# (browsers reject wildcard origin when credentials are allowed) and is a
# security anti-pattern. Scope this to the actual frontend origin(s) instead.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "platform": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)