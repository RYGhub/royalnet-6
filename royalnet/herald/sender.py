import royalnet.royaltyping as t
import logging
import websockets
import pydantic
import contextlib

from . import models, exc

log = logging.getLogger(__name__)
Model = t.TypeVar("Model", pydantic.BaseModel)


class Sender:
    instance_count = 0

    def __init__(
            self,
            secret: str,
    ):
        self.secret: str = secret

        self.instance_count += 1
        self.instance_number = self.instance_count
        self.log = logging.getLogger(f"{__name__}.Sender.{self.instance_number}")

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

    @contextlib.asynccontextmanager
    async def _connect(self, uri):
        async with websockets.connect(uri) as websocket:
            connection = Connection(websocket=websocket)

            try:
                yield websocket
            except exc.Closed as close:
                await websocket.close(code=close.code, reason=close.reason)


class Connection:
    instance_count = 0

    def __init__(self, websocket: websockets.WebSocketClientProtocol):
        self.websocket: websockets.WebSocketClientProtocol = websocket

        self.instance_count += 1
        self.instance_number = self.instance_count
        self.log = logging.getLogger(f"{__name__}.Connection.{self.instance_number}")

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

    async def authenticate(self, secret: str):
        await self.send(models.AuthModel(secret=secret))

    async def recv(self, model: t.Type[Model]) -> Model:
        self._info(f"Expecting to receive a {model.__qualname__!r}")

        self._debug(f"Waiting...")
        try:
            data = await self.websocket.recv()
        except websockets.ConnectionClosed:
            raise exc.Closed(code=1000, reason="Connection was closed.")

        self._debug(f"Interpreting data as a {model.__qualname__!r}")
        try:
            return model.parse_raw(data)
        except pydantic.ValidationError as e:
            self._warning(f"Received malformed packet ({e!r})")
            raise exc.Closed(code=1002, reason="Packet validation error, see server console.")

    async def send(self, obj: Model) -> None:
        self._info(f"Trying to send a {obj.__class__.__qualname__!r}")

        self._debug(f"Converting {obj!r} to JSON...")
        data = obj.json()

        self._debug(f"Sending data...")
        await self.websocket.send(data)
