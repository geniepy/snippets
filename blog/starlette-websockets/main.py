import logging

from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)

class HelloEndpoint(HTTPEndpoint):
    def get(self, request: Request):
        return Response("<h1>Hello, World!</h1>")

class WSEndpoint(WebSocketEndpoint):
    encoding = "bytes"

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()

        logger.info(f"Connected: {websocket}")

    async def on_receive(self, websocket: WebSocket, data: bytes):
        await websocket.send_bytes(b"OK!")

        logger.info("websockets.received")

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        logger.info(f"Disconnected: {websocket}")

instance = Starlette(
    routes=(
        Route("/hello", HelloEndpoint, name="hello"),
        WebSocketRoute("/ws", WSEndpoint, name="ws"),
    ),
)
