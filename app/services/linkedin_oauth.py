from urllib.parse import urlencode

import httpx

from app.core.config import settings

AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
SCOPES = "openid profile email"


def build_authorization_url(state: str) -> str:
    if not settings.linkedin_client_id:
        raise NotImplementedError("LinkedIn OAuth client credentials are not configured")
    params = {
        "response_type": "code",
        "client_id": settings.linkedin_client_id,
        "redirect_uri": settings.resolved_linkedin_redirect_uri,
        "state": state,
        "scope": SCOPES,
    }
    return f"{AUTHORIZATION_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    if not settings.linkedin_client_id or not settings.linkedin_client_secret:
        raise NotImplementedError("LinkedIn OAuth client credentials are not configured")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.resolved_linkedin_redirect_uri,
        "client_id": settings.linkedin_client_id,
        "client_secret": settings.linkedin_client_secret,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


async def fetch_linkedin_userinfo(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
    response.raise_for_status()
    return response.json()
