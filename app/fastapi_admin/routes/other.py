from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_409_CONFLICT
from starlette.templating import Jinja2Templates

from ..common import pwd_context
from ..depends import get_current_user
from ..schemas import UpdatePasswordIn
from ...settings.config import settings

templates = Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)

router = APIRouter()


@router.put("/password")
async def update_password(update_password_in: UpdatePasswordIn, user=Depends(get_current_user)):
    if update_password_in.new_password != update_password_in.confirm_password:
        raise HTTPException(HTTP_409_CONFLICT, detail="Incorrect Confirm Password!")
    if not pwd_context.verify(update_password_in.old_password, user.password):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Incorrect Password!")
    user.password = pwd_context.hash(update_password_in.new_password)
    await user.save(update_fields=["password"])
    return {"success": True}


@router.get("/home")
async def home():
    return {"html": templates.get_template("home.html").render()}
