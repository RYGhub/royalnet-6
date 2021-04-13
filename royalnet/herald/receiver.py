import royalnet.royaltyping as t
import logging
import websockets
import json
import pydantic

from . import models, exc

log = logging.getLogger(__name__)
Model = t.TypeVar("Model", pydantic.BaseModel)


class Receiver:
    def __init__(
            self,
            secret: str,
            model: t.Type[Model],
            callback: t.Callable[[websockets.WebSocketServerProtocol, str, Model], t.Awaitable[None]],
            oneshot: bool = False
    ):
        self.secret: str = secret
        self.model: t.Type[Model] = model
        self.callback: t.Callable[[websockets.WebSocketServerProtocol, str, Model], t.Awaitable[None]] = callback
        self.oneshot: bool = oneshot

    async def _recv(self, websocket: websockets.WebSocketServerProtocol, model: t.Type[Model]) -> Model:
        log.info(f"{self!r}: Expecting to receive a {model.__qualname__!r}")

        log.debug(f"{self!r}: Waiting...")
        data = await websocket.recv()

        log.debug(f"{self!r}: Interpreting data as a {model.__qualname__!r}")
        try:
            return model.parse_raw(data)
        except pydantic.ValidationError as e:
            log.warning(f"{self!r}: Received malformed packet ({e!r})")
            raise exc.Closed(code=1002, reason="Packet validation error, see server console.")

    async def _send(self, websocket: websockets.WebSocketServerProtocol, obj: Model) -> None:
        log.info(f"{self!r}: Trying to send a {obj.__class__.__qualname__!r}")

        log.debug(f"{self!r}: Converting {obj!r} to JSON...")
        data = obj.json()

        log.debug(f"{self!r}: Sending data...")
        await websocket.send(data)

    async def _authenticate(self, websocket: websockets.WebSocketServerProtocol) -> None:
        log.debug(f"{self!r}: Waiting for authentication packet...")
        auth = await self._recv(websocket=websocket, model=models.AuthModel)
        log.debug(f"{self!r}: Received authentication packet {auth!r}!")

        if auth.secret != self.secret:
            log.warning(f"Received invalid secret {auth.secret!r}, terminating with close code 1008...")
            raise exc.Closed(code=1008, reason=f"Invalid secret.")

        log.debug("Authentication successful!")

    async def _dataloop(self, websocket: websockets.WebSocketServerProtocol, path: str) -> None:
        data = await self._recv(websocket=websocket, model=self.model)
        log.debug(f"{self!r}: Triggering callback with {data!r}")
        await self.callback(websocket, path, data)

    async def _listener(self, websocket: websockets.WebSocketServerProtocol, path: str):
        log.info(f"{self!r}: Starting new connection...")

        try:
            if path != "/":
                log.warning(f"Received connection with unexpected path {path!r}, terminating with close code 1010...")
                raise exc.Closed(code=1010, reason=f"Unexpected path: {path!r}")
            else:
                log.debug(f"Path is: {path!r}")

            await self._authenticate(websocket=websocket)

            if self.oneshot:
                log.debug(f"Listening for a single data packet...")
                await self._dataloop(websocket=websocket, path=path)
            else:
                log.debug(f"Listening for data packets until socket closure...")
                while True:
                    await self._dataloop(websocket=websocket, path=path)

            raise exc.Closed(code=1000, reason="Data transfer complete!")

        except exc.Closed as close:
            log.info(f"{self!r}: Closing connection because {close!r} was raised...")
            await websocket.close(code=close.code, reason=close.reason)
            log.debug(f"Connection closed successfully!")
