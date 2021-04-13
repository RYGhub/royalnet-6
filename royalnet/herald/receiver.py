import royalnet.royaltyping as t
import logging
import websockets
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
        self.log = logging.getLogger(f"{__name__}.Receiver.{self.instance_number}")

    def _debug(self, *args, **kwargs) -> None:
        return self.log.debug(*args, **kwargs)

    def _info(self, *args, **kwargs) -> None:
        return self.log.info(*args, **kwargs)

    def _warning(self, *args, **kwargs) -> None:
        return self.log.warning(*args, **kwargs)

    def _error(self, *args, **kwargs) -> None:
        return self.log.error(*args, **kwargs)

    def _fatal(self, *args, **kwargs) -> None:
        return self.log.fatal(*args, **kwargs)

    async def _recv(self, websocket: websockets.WebSocketServerProtocol, model: t.Type[Model]) -> Model:
        self._info(f"Expecting to receive a {model.__qualname__!r}")

        self._debug(f"Waiting...")
        try:
            data = await websocket.recv()
        except websockets.ConnectionClosed:
            raise exc.Closed(code=1000, reason="Connection was closed.")

        self._debug(f"Interpreting data as a {model.__qualname__!r}")
        try:
            return model.parse_raw(data)
        except pydantic.ValidationError as e:
            raise exc.Closed(code=1002, reason=f"Packet validation error, expected {model!r}.")

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
            raise exc.Closed(code=1008, reason=f"Invalid secret.")

        self._debug("Authentication successful!")

    async def _checkpath(self, path: str):
        if path != "/":
            self._warning(f"Received connection with unexpected path {path!r}, terminating with close code 1010...")
            raise exc.Closed(code=1010, reason=f"Unexpected path: {path!r}")
        else:
            self._debug(f"Path is: {path!r}")

    async def _dataloop(self, websocket: websockets.WebSocketServerProtocol, path: str) -> None:
        data = await self._recv(websocket=websocket, model=self.model)
        self._debug(f"Triggering callback with {data!r}")
        await self.callback(websocket, path, data)

    async def _dataget(self, websocket: websockets.WebSocketServerProtocol, path: str):
        if self.oneshot:
            self._debug(f"Listening for a single data packet...")
            await self._dataloop(websocket=websocket, path=path)
        else:
            self._debug(f"Listening for data packets until socket closure...")
            while True:
                await self._dataloop(websocket=websocket, path=path)

    async def _close(self, websocket: websockets.WebSocketServerProtocol, close: exc.Closed):
        if close.code != 1000:
            self._warning(f"Closing connection: {close.code} - {close.reason}")
        else:
            self._info(f"Closing connection...")
        await websocket.close(code=close.code, reason=close.reason)
        self._debug(f"Connection closed successfully!")

    async def _listener(self, websocket: websockets.WebSocketServerProtocol, path: str):
        self._info(f"Starting new connection...")

        try:
            await self._checkpath(path=path)
            await self._authenticate(websocket=websocket)
            await self._dataget(websocket=websocket, path=path)
            raise exc.Closed(code=1000, reason="Data transfer complete!")

        except exc.Closed as close:
            await self._close(websocket=websocket, close=close)
