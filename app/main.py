from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, candidate, organization, profile, quiz, user
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    # Interactive docs can be switched off with DOCS_ENABLED=false.
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
    # Makes "Try it out" in /docs hit the deployed host, not localhost.
    servers=[{"url": settings.base_url, "description": settings.environment.value}],
)

_allow_all_origins = "*" in settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Browsers reject credentialed requests against a wildcard origin, and
    # this API authenticates with bearer tokens rather than cookies.
    allow_credentials=not _allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz.router, prefix=settings.api_prefix)
app.include_router(user.router, prefix=settings.api_prefix)
app.include_router(organization.router, prefix=settings.api_prefix)
app.include_router(candidate.router, prefix=settings.api_prefix)
app.include_router(profile.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment.value}
