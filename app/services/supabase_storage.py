import httpx

from app.core.config import settings


def _require_config() -> None:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise NotImplementedError("Supabase storage is not configured")


async def create_signed_upload_url(path: str) -> dict:
    """Ask Supabase Storage for a URL the client can upload the CV PDF to
    directly, so the backend never has to receive/hold the file itself.

    Uses the "create signed upload URL" Storage API:
    POST /storage/v1/object/upload/sign/{bucket}/{path} -> {url, token}
    The returned url is relative and already carries the upload token.
    """
    _require_config()
    endpoint = (
        f"{settings.supabase_url}/storage/v1/object/upload/sign/"
        f"{settings.supabase_cv_bucket}/{path}"
    )
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(endpoint, headers=headers, json={})
    response.raise_for_status()
    data = response.json()
    return {
        "upload_url": f"{settings.supabase_url}/storage/v1{data['url']}",
        "token": data.get("token"),
        "path": path,
    }
