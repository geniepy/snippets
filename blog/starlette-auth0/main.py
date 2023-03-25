from urllib.parse import quote_plus, urlencode
from textwrap import dedent

from authlib.integrations.starlette_client import OAuth
from starlette.applications import Starlette
from starlette.config import Config
from starlette.endpoints import HTTPEndpoint
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

# define config

config = Config(".env")

AUTH0_CLIENT_ID = config("AUTH0_CLIENT_ID")

AUTH0_CLIENT_SECRET = config("AUTH0_CLIENT_SECRET")

AUTH0_DOMAIN = config("AUTH0_DOMAIN")

# initialise OAuth

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=(
        f"https://{AUTH0_DOMAIN}/.well-known/openid-configuration"
    ),
)

# HTTP endpoints

class IndexEndpoint(HTTPEndpoint):
    def get(self, request: Request) -> Response:
        user_id = request.session.get("AUTH0_USER")

        if user_id:
            return Response(
                dedent(
                    f"""
                    <h1>Hello {user_id}!</h1>
                    <a href="/auth/logout">Logout</a>
                    """
                )
            )
        else:
            return Response(
                dedent(
                    """
                    <h1>Hello World!</h1>
                    <a href="/auth/login">Login</a>
                    """
                )
            )

class LoginEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        return await oauth.auth0.authorize_redirect(
            request, "http://localhost:8000/auth/callback"
        )

class CallbackEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        token = await oauth.auth0.authorize_access_token(request)

        user_info = token.get("userinfo")
        if user_info:
            request.session["AUTH0_USER"] = user_info["sub"]

        return RedirectResponse("/")

class LogoutEndpoint(HTTPEndpoint):
    async def get(self, request: Request):
        if "AUTH0_USER" in request.session:
            del request.session["AUTH0_USER"]

        params = urlencode(
            {
                "returnTo": "http://localhost:8000",
                "client_id": AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        )

        return RedirectResponse(f"https://{AUTH0_DOMAIN}/v2/logout?{params}")

# Starlette

instance = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key="secret"),
    ],
    routes=(
        Route("/", IndexEndpoint, name="index"),
        Mount(
            "/auth",
            routes=(
                Route("/login", LoginEndpoint, name="auth:login"),
                Route("/callback", CallbackEndpoint, name="auth:callback"),
                Route("/logout", LogoutEndpoint, name="auth:logout"),
            ),
        ),
    ),
)
