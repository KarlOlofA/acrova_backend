"""Local and container entrypoint.

Reads HOST / PORT / ENVIRONMENT from the environment (see .env.example), so
the same command works for local dev and on DigitalOcean:

    uv run main.py

DigitalOcean's Python buildpack installs into its own virtualenv rather than
./.venv, so the deployed run command adds two flags to reuse it as-is:

    uv run --active --no-sync main.py
"""

import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload_enabled,
        log_level=settings.effective_log_level,
    )
