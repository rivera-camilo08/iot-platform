from datetime import datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field("bearer")


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str
