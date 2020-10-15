from datetime import timedelta

from fastapi import APIRouter, Body, HTTPException, BackgroundTasks, Depends

from app.applications.users.models import User
from app.applications.users.utils import update_last_login
from app.core.auth.schemas import JWTToken, Msg, OAuth2PasswordRequestForm
from app.core.auth.utils.contrib import (generate_password_reset_token, send_reset_password_email,
                                         verify_password_reset_token, authenticate_user,
                                         )
from app.core.auth.utils.jwt import create_access_token
from app.core.auth.utils.password import get_password_hash
from app.settings.config import settings

router = APIRouter()


@router.post("/access-token", response_model=JWTToken, description="登录", summary="登录")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    登录接口
    :param form_data:
    :return:
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if user:
        await update_last_login(user.id)
    elif not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"user_id": user.id}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/password-recovery/{email}", response_model=Msg, description="找回密码", summary="找回密码")
async def recover_password(email: str, background_tasks: BackgroundTasks):
    """
    找回密码
    """
    user = await User.get_by_email(email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户名无效",
        )
    password_reset_token = generate_password_reset_token(email=email)
    background_tasks.add_task(send_reset_password_email, email_to=user.email, email=email, token=password_reset_token)
    return {"msg": "密码已发送至电子邮件"}


@router.post("/reset-password/", response_model=Msg, description="修改密码", summary="修改密码")
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    """
    修改密码
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="令牌无效")
    user = await User.get_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not User.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    await user.save()
    return {"msg": "Password updated successfully"}
