from typing import List

from fastapi import Depends, HTTPException
from freddie import ViewSet
from freddie.viewsets import FieldedViewset, PaginatedListViewset, route, FilterableListViewset

from app.applications.users.models import User
from app.applications.users.schemas import BaseUser, BaseUserOut, BaseUserUpdate
from app.core.auth.utils.contrib import get_current_active_user
from app.core.auth.utils.password import get_password_hash


class UserViewSet(
    FieldedViewset,
    PaginatedListViewset,
    FilterableListViewset,
    ViewSet
):
    """
    https://github.com/tinkoffjournal/freddie
    预定义的基于类的视图集，用于基本的REST API操作
    """
    schema = BaseUser

    class Paginator:
        default_limit = 10
        max_limit = 100

    class Filter:
        username: str = None

    def get_openapi_tags(self) -> List[str]:
        return []

    async def list(self, *, filter_by, paginator, fields, request, current_user: User = Depends(get_current_active_user)):
        print(filter_by, "筛选字段")
        users = await User.all().limit(paginator.limit).offset(paginator.offset)
        return users

    async def retrieve(self, pk, *, fields, request):
        user = await User.get(id=pk)
        if not user:
            raise HTTPException(
                status_code=400, detail="The user doesn't have enough privileges"
            )
        return user

    async def create(self, body, *, request):
        return body

    async def update(self, pk, body, *, request):
        # updated_post = post.copy()
        # for key, value in body.dict(exclude_unset=True).items():
        #     setattr(updated_post, key, value)
        # return updated_post
        return None

    async def destroy(self, pk, *, request):
        pass

    # Add custom handler on /meta path
    @route(detail=False, summary='List metadata')
    async def meta(self):
        """
        详情
        """
        return None

    @route(detail=False, summary='更新自己的用户', path="/me", methods=["PUT"], response_model=BaseUserOut, status_code=200)
    async def retrieve_meta(self, user_in: BaseUserUpdate, current_user: User = Depends(get_current_active_user)):
        """
        更新自己的用户
        """
        if user_in.password is not None and user_in.password != "string":
            hashed_password = get_password_hash(user_in.password)
            current_user.hashed_password = hashed_password
        if user_in.username is not None and user_in.password != "string":
            current_user.username = user_in.username
        if user_in.email is not None and user_in.password != "user@example.com":
            current_user.email = user_in.email
        current_user.first_name = user_in.first_name
        current_user.last_name = user_in.last_name
        await current_user.save()
        return current_user
