from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import Response

from app.utils.models import AppRequest


class AdminAuth(AuthenticationBackend):
    async def login(
        self,
        request: Request,
    ) -> bool:
        form = await request.form()
        username, password = form['username'], form['password']

        if (
            username == request.state.env_settings.su_username.get_secret_value()
            and password == request.state.env_settings.su_password.get_secret_value()
        ):
            request.session.update({'token': 'admin'})
            return True
        return False

    async def logout(
        self,
        request: Request,
    ) -> Response | bool:
        request.session.clear()
        return True

    async def authenticate(
        self,
        request: Request,
    ) -> Response | bool:
        token = request.session.get('token')
        if not token or token != 'admin':
            return False
        return True
