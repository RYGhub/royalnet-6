import royalnet.royaltyping as t
import logging
import websockets
import json
import pydantic

from . import models, exc

log = logging.getLogger(__name__)
Model = t.TypeVar("Model", pydantic.BaseModel)


class Receiver:
    instance_count = 0
    
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
        
        self.instance_count += 1
        self.instance_number = self.instance_count
        self.log = logging.getLogger(f"{__name__}.{self.instance_number}")
        
    def _debug(self, *args, **kwargs):
        self.log.debug(*args, **kwargs)
        
    def _info(self, *args, **kwargs):
        self.log.info(*args, **kwargs)
        
    def _warning(self, *args, **kwargs):
        self.log.warning(*args, **kwargs)
        
    def _error(self, *args, **kwargs):
        self.log.error(*args, **kwargs)
        
    def _fatal(self, *args, **kwargs):
        self.log.fatal(*args, **kwargs)

    async def _recv(self, websocket: websockets.WebSocketServerProtocol, model: t.Type[Model]) -> Model:
        self._info(f"Expecting to receive a {model.__qualname__!r}")

        self._debug(f"Waiting...")
        data = await websocket.recv()

        self._debug(f"Interpreting data as a {model.__qualname__!r}")
        try:
            return model.parse_raw(data)
        except pydantic.ValidationError as e:
            self._warning(f"Received malformed packet ({e!r})")
            raise exc.Closed(code=1002, reason="Packet validation error, see server console.")

    async def _send(self, websocket: websockets.WebSocketServerProtocol, obj: Model) -> None:
        self._info(f"Trying to send a {obj.__class__.__qualname__!r}")

        self._debug(f"Converting {obj!r} to JSON...")
        data = obj.json()

        self._debug(f"Sending data...")
        await websocket.send(data)

    async def _authenticate(self, websocket: websockets.WebSocketServerProtocol) -> None:
        self._debug(f"Waiting for authentication packet...")
        auth = await self._recv(websocket=websocket, model=models.AuthModel)
        self._debug(f"Received authentication packet {auth!r}!")

        if auth.secret != self.secret:
            self._warning(f"Received invalid secret {auth.secret!r}, terminating with close code 1008...")
            raise exc.Closed(code=1008, reason=f"Invalid secret.")

        self._debug("Authentication successful!")

    async def _dataloop(self, websocket: websockets.WebSocketServerProtocol, path: str) -> None:
        data = await self._recv(websocket=websocket, model=self.model)
        self._debug(f"Triggering callback with {data!r}")
        await self.callback(websocket, path, data)

    async def _listener(self, websocket: websockets.WebSocketServerProtocol, path: str):
        self._info(f"Starting new connection...")

        try:
            if path != "/":
                self._warning(f"Received connection with unexpected path {path!r}, terminating with close code 1010...")
                raise exc.Closed(code=1010, reason=f"Unexpected path: {path!r}")
            else:
                self._debug(f"Path is: {path!r}")

            await self._authenticate(websocket=websocket)

            if self.oneshot:
                self._debug(f"Listening for a single data packet...")
                await self._dataloop(websocket=websocket, path=path)
            else:
                self._debug(f"Listening for data packets until socket closure...")
                while True:
                    await self._dataloop(websocket=websocket, path=path)

            raise exc.Closed(code=1000, reason="Data transfer complete!")

        except exc.Closed as close:
            self._info(f"Closing connection because {close!r} was raised...")
            await websocket.close(code=close.code, reason=close.reason)
            self._debug(f"Connection closed successfully!")
