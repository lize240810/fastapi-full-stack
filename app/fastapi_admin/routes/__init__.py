from fastapi import Depends

from ..depends import jwt_required
from ..factory import app
from . import other, rest, site
# from app.core.auth.utils.contrib import get_current_active_user

app.include_router(site.router, tags=['项目配置'])
app.include_router(other.router, dependencies=[Depends(jwt_required)], tags=['主页'])
app.include_router(rest.router, dependencies=[Depends(jwt_required)], prefix="/rest")
