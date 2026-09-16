from app.schemas.common import ORMModel
from app.schemas.user import UserRead


class LinkedInLoginResponse(ORMModel):
    authorization_url: str
    state: str


class TokenResponse(ORMModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
