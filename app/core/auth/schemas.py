from typing import Optional

from fastapi import Form, Body
from pydantic import BaseModel


class CredentialsSchema(BaseModel):
    username: Optional[str]
    email: Optional[str] = None
    password: str


class JWTToken(BaseModel):
    access_token: str
    token_type: str


class JWTTokenData(BaseModel):
    username: str = None


class JWTTokenPayload(BaseModel):
    user_id: int = None


class Msg(BaseModel):
    msg: str


class PasswordRequest(BaseModel):
    username: str = Body(..., description="用户名")
    password: str = Body(..., description="密码")


class OAuth2PasswordRequestForm:
    """
    获取用户username和密码的form表单
    """

    def __init__(
            self,
            # grant_type: str = Form(None, regex="password"),
            username: str = Form(..., description="用户名"),
            password: str = Form(..., description="密码"),
    ):
        # self.grant_type = grant_type
        self.username = username
        self.password = password
