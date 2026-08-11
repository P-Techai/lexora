from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.1.0-foundation",
)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return HealthResponse(
        status="healthy",
        app_name="LÉXORA (LXR)",
        version="0.1.0-foundation"
    )
