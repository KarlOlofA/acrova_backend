from fastapi import FastAPI

from app.api.routes import quiz, tests
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(quiz.router, prefix=settings.api_prefix)
app.include_router(tests.router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
