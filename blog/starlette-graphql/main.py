from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response
from strawberry.asgi import GraphQL
from strawberry.types import Info
import strawberry

@dataclass
class DBUser:
    email: str
    first_name: str
    last_name: str
    created_at: datetime

@strawberry.type
class User:
    email: str
    first_name: str
    last_name: str
    created_at: datetime

def get_user_from_database(request: Request) -> Optional[DBUser]:
    return DBUser(
        email="batman@example.com",
        first_name="Bruce",
        last_name="Wayne",
        created_at=datetime.now(),
    )

def resolve_current_user(root: User, info: Info) -> Optional[User]:
    request = info.context["request"]

    user = get_user_from_database(request)

    if not user:
        return None

    return User(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at,
    )

@strawberry.type
class Query:
    current_user: User = strawberry.field(resolver=resolve_current_user)

def resolve_message() -> str:
    return "Hello!"

@strawberry.type
class Query:
    message: str = strawberry.field(resolver=resolve_message)
    current_user: User = strawberry.field(resolver=resolve_current_user)


class HelloEndpoint(HTTPEndpoint):
    def get(self, request: Request):
        return Response("<h1>Hello, World!</h1>")

instance = Starlette(
    routes=(
        Route("/hello", HelloEndpoint, name="hello"),
    ),
)

schema = strawberry.Schema(Query)

graphql_app = GraphQL(schema)

instance.add_route("/graphql", graphql_app)
instance.add_websocket_route("/graphql", graphql_app)
