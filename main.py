"""Local and container entrypoint.

Reads HOST / PORT / ENVIRONMENT from the environment (see .env.example), so
the same command works for local dev and on DigitalOcean:

    python main.py
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
