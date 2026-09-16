from fastapi import FastAPI

from app.api.routes import auth, candidate, organization, profile, quiz, user
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(quiz.router, prefix=settings.api_prefix)
app.include_router(user.router, prefix=settings.api_prefix)
app.include_router(organization.router, prefix=settings.api_prefix)
app.include_router(candidate.router, prefix=settings.api_prefix)
app.include_router(profile.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok"}
