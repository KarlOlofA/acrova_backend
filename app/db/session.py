from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _normalize_database_url(url: str) -> str:
    """DigitalOcean (and most Postgres hosts) hand out postgres:// or
    postgresql:// URLs, which default to psycopg2. We install psycopg
    (v3) instead, so rewrite the scheme to use it explicitly.
    """
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


# Engine options tuned for a pooled Postgres (Supabase runs Supavisor):
#
# prepare_threshold=None turns off psycopg's automatic prepared statements.
# Session mode (port 5432 on the pooler host) tolerates them, but transaction
# mode (6543) hands each transaction a different backend, so a statement
# prepared on one is absent on the next and queries fail with
# 'prepared statement "_pg3_0" does not exist'. Disabling them costs little at
# this scale and makes the port in DATABASE_URL a non-decision.
#
# pool_pre_ping discards connections the pooler closed while idle rather than
# raising on the first query after a quiet period.
_url = _normalize_database_url(settings.database_url)
_engine_kwargs: dict = {"pool_pre_ping": True}
if _url.startswith("postgresql+psycopg://"):
    _engine_kwargs["connect_args"] = {"prepare_threshold": None}

engine = create_engine(_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
