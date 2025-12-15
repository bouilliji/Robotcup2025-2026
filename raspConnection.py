import json
import serial_asyncio


class Connection:

    class Message:

        def __init__(self, ordre: str, data):
            self.ordre = ordre
            self.data = data

        def __str__(self):
            return f"{self.ordre}\r\n{json.dumps(self.data)}"

        def __len__(self):
            return len(str(self))

    def __init__(self, port: str):

        async def _defaultRaw(data: bytes):
            print("Raw data received but no handler")

        async def _defaultMessage(ordre: str, data):
            print(f"Message received but no handler for ordre {ordre}")

        self.port = port
        self.toSend = []
        self.running = False
        self.onRaw = _defaultRaw
        self.onMessage = _defaultMessage
        self.handlers = dict()

    def on(self, ordre: str):

        def decorator(func):
            self.handlers[ordre] = func
            return func

        return decorator

    def default(self):

        def decorator(func):
            self.onMessage = func
            return func

        return decorator

    def raw(self):

        def decorator(func):
            self.onRaw = func
            return func

        return decorator

    async def send(self, ordre: str, data) -> None:
        self.toSend.append(Connection.Message(ordre, data))

    async def sendRaw(self, data) -> None:
        self.toSend.append(data)

    async def isRunning(self) -> bool:
        return self.running

    async def isLate(self) -> bool:
        return len(self.toSend) > 10

    async def start(self) -> None:
        self.running = True
        reader, writer = await serial_asyncio.open_serial_connection(
            url=self.port, baudrate=115200)
        writer.write(b"PING")
        await writer.drain()
        while self.running:
            data = await reader.readexactly(4)
            if data == b"PING":
                pass
            elif data[:2] == b"DAT":
                size = int(await reader.readexactly(int(data[2:]) + 6))
                data = str(await reader.readexactly(size))
                ordre, donnee = data.split("\r\n")
                if ordre in self.handlers:
                    await self.handlers[ordre](json.loads(donnee))
                elif self.onMessage is not None:
                    await self.onMessage(ordre, json.loads(donnee))
                else:
                    print(
                        f"Warning: ordre {ordre} not found and no default handler"
                    )
            elif data[:2] == b"RAW":
                size = int(await reader.readexactly(int(data[2:]) + 6))
                data = await reader.readexactly(size)
                if self.onRaw is not None:
                    await self.onRaw(data)
                else:
                    print("Warning: raw data received but no raw handler")
            elif data[:2] == b"EXT":
                self.running = False
                return data[2:]
            if len(self.toSend) > 0:
                data = self.toSend.pop(0)
                if isinstance(data, Connection.Message):
                    size = len(data)
                    if size > 1e9:
                        print(
                            "Warning: data too big message not sended, size > 1e9"
                        )
                        continue
                    writer.write(
                        f"DAT{len(str(size))}\r\n{size}\r\n\r\n{data}".encode(
                            "utf-8"))
                else:
                    size = len(data)
                    if size > 1e9:
                        print(
                            "Warning: data too big message not sended, size > 1e9"
                        )
                        continue
                    if isinstance(data, str):
                        data = data.encode("utf-8")
                    writer.write(f"RAW{len(str(size))}\r\n{size}\r\n\r\n".
                                 encode("utf-8") + data)
            else:
                writer.write(b"PING")
            await writer.drain()

        writer.write(b"EXT0")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def stop(self):
        self.running = False
