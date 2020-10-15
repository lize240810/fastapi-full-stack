from fastapi import FastAPI

from app.core.exceptions import SettingNotFound
from app.core.init_app import configure_logging, init_middlewares, register_db, register_exceptions, register_routers
from app.fastapi_admin.factory import app as admin_app
from app.fastapi_admin.site import Site, Menu

try:
    from app.settings.config import settings
except ImportError:
    raise SettingNotFound('Can not import settings. Create settings file from template.config.py')

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.VERSION,
)
app.mount('/admin', admin_app)

configure_logging()
init_middlewares(app)
register_db(app)
register_exceptions(app)
register_routers(app)


@app.on_event('startup')
async def startup():
    await admin_app.init(
        admin_secret="test",
        permission=True,
        # login_view="app.core.auth.routers.login.login_for_access_token",
        site=Site(
            name="后台管理",
            login_footer="FASTAPI ADMIN 项目",
            login_description="FastAPI Admin 控制台",
            locale="zh-CN",
            locale_switcher=True,
            theme_switcher=True,
            menus=[
                Menu(name="首页", url="/", icon="fa fa-home"),
                Menu(
                    name="内容",
                    children=[
                        Menu(
                            name="Config",
                            url="/rest/Config",
                            icon="fa fa-gear",
                            import_=True,
                            search_fields=("key",),
                        ),
                        Menu(
                            name="Product",
                            url="/rest/Product",
                            icon="fa fa-table",
                            search_fields=("name",),
                        ),
                    ],
                ),
                Menu(
                    name="外部",
                    children=[
                        Menu(
                            name="Github",
                            url="https://github.com/long2ice/fastapi-admin",
                            icon="fa fa-github",
                            external=True,
                        ),
                    ],
                ),
                Menu(
                    name="权限",
                    children=[
                        Menu(
                            name="用户",
                            url="/rest/User",
                            icon="fa fa-user",
                            attrs={"created_at": {"label": "创建时间"}, "email": {"label": "邮箱"}},
                            sort_fields=("created_at",),
                            exclude=('updated_at', 'password_hash', 'hashed_id', 'avatar'),
                            search_fields=("username",),
                        ),
                        Menu(name="Role", url="/rest/Role", icon="fa fa-group", ),
                        Menu(name="Permission", url="/rest/Permission", icon="fa fa-user-plus", ),
                        Menu(
                            name="AdminLog",
                            url="/rest/AdminLog",
                            icon="fa fa-align-left",
                            search_fields=("action", "admin", "model"),
                        ),
                        Menu(name="Logout", url="/logout", icon="fa fa-lock", ),
                    ],
                ),
            ],
        ),
    )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host='0.0.0.0', port=8000, debug=settings.DEBUG, reload=True, lifespan="on")
