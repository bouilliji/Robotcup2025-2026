import json
import logging
import serial_asyncio

# Create handler to show log
console = logging.StreamHandler()
console.setLevel(logging.INFO)  # Set console to info level

logging.getLogger("").addHandler(console)


class Connection:
    """Connection class to communicate with the raspberry pi

    Attributes:
        port {str} -- port to connect to
        toSend {list} -- message queue
        state {int} -- 0 = running, 1 = stopped, 2 = error
        onRaw {function} -- function to call when raw data is received
        onMessage {function} -- function to call when ordonated data is received
        handlers {dict} -- dictionary of functions to call when ordonated data is received
        exitCode {int} -- exit code to send when stopping the connection
        dbLevel {DebugLevel} -- debug level

    Methods:
        __init__(port: str) -> None: create a new connection
        on(ordre: str) -> function: decorator to add a handler
        default() -> function: decorator to add a default handler
        raw() -> function: decorator to add a raw handler
        send(ordre: str, data) -> None: send ordonated data
        sendRaw(data) -> None: send raw data
        isRunning() -> bool: verify if the connection is still running
        isLate() -> bool: verify if there is too many messages in the queue
        start(baudrate: int) -> int: start the connection and listen for data
        stop(code: int) -> None: stop the connection and send a exit signal
    """

    class Message:
        """Message class to send ordonated data to the raspberry pi

        Attributes:
            ordre {str} -- ordre to send
            data {any} -- data to send

        Methods:
            __init__(ordre: str, data) -> None: create a new message
            __str__() -> str: return the message as a string
            __len__() -> int: return the length of the message
            __rep__() -> str: return the message as a string
        """

        def __init__(self, ordre: str, data):
            if not isinstance(ordre, str):
                raise TypeError("Error: ordre must be a string")
            self.ordre = ordre
            self.data = data

        def __str__(self):
            return f"{self.ordre}\r\n{json.dumps(self.data)}"

        __rep__ = __str__

        def __len__(self):
            return len(str(self))

    def __init__(self, port: str):
        """Create a new connection
        Arguments:
            port {str} -- port to connect to
        Raises:
            TypeError: if either port is not a string or dbLevel is not a DebugLevel
        """

        async def _defaultRaw(_):
            logging.warning("No handler for raw data")

        async def _defaultMessage(ordre: str, _):
            logging.warning(f"No handler for ordre {ordre} and no default handler")

        self.port = port
        self.toSend = []
        self.state = 1  # 0 = running, 1 = stopped, 2 = error
        self.exitCode = 0

        # functions to call when data is received
        self.onRaw = _defaultRaw
        self.onMessage = _defaultMessage
        self.handlers = dict()

    def on(self, ordre: str):
        """Decorator to add a handler for a specific ordre
        Arguments:
            ordre {str} -- ordre to add a handler for
        Raises:
            TypeError: if ordre is not a string
        """
        if not isinstance(ordre, str):
            raise TypeError("Error: ordre must be a string")

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

    async def send(self, ordre: str, data) -> None:  # used to send ordonated data
        """Send ordonated data to the raspberry pi
        Arguments:
            ordre {str} -- ordre to send
            data {any} -- data to send
        Raises:
            TypeError: if ordre is not a string
        """
        if not isinstance(ordre, str):
            raise TypeError("Error: ordre must be a string")
        self.toSend.append(Connection.Message(ordre, data))

    async def sendRaw(self, data) -> None:
        """Send raw data to the raspberry pi
        Arguments:
            data {bytes} -- data to send
        Raises:
            TypeError: if data is not bytes
        """
        if not isinstance(data, bytes):
            raise TypeError("Error: raw data must be bytes")
        self.toSend.append(data)

    async def isRunning(self) -> bool:
        """Verify if the connection is still running
        Returns:
            bool -- True if the connection is still running
        """
        return self.state == 0

    async def isLate(self) -> bool:  # to many messages are in the queue
        """Verify if there is too many messages in the queue
        Returns:
            bool -- True if there is too many messages in the queue
        """
        return len(self.toSend) > 10

    async def start(self, baudrate: int = 115200) -> int:
        """Start the connection and listen for data
        Arguments:
            baudrate {int} -- baudrate of the serial connection (default: {115200})

        Returns:
            int -- exit code

        Raises:
            serial.*: if the serial connection fails
            TypeError: if baudrate is not an integer
        """
        if not isinstance(baudrate, int):
            raise TypeError("Error: baudrate must be an integer")

        # open serial connection
        reader, writer = await serial_asyncio.open_serial_connection(
            url=self.port, baudrate=baudrate
        )

        self.state = 0

        # send first ping
        writer.write(b"PING")
        await writer.drain()

        # listen for data
        while self.isRunning():
            data = await reader.readexactly(4)
            logging.info(f"Packet received: {data}")

            if data == b"PING":
                pass

            elif data[:2] == b"DAT":
                # read data
                size = int(await reader.readexactly(int(data[2:]) + 6))
                data = str(await reader.readexactly(size))
                ordre, donnee = data.split("\r\n")

                logging.info(f"Data received: {ordre}\r\n{donnee}")

                # call the right handler function
                if ordre in self.handlers:
                    await self.handlers[ordre](json.loads(donnee))
                else:
                    await self.onMessage(ordre, json.loads(donnee))
            elif data[:2] == b"RAW":
                size = int(await reader.readexactly(int(data[2:]) + 6))
                data = await reader.readexactly(size)

                logging.info(f"Raw data received: \r\n{data}")

                await self.onRaw(data)

            elif data[:2] == b"EXT":
                logging.info(f"Exited with code: {data[2:]}")

                self.state = (data[2:] == b"0") + 1
                return int(str(data[2:]))

            elif len(self.toSend) > 0:
                data = self.toSend.pop(0)
                if isinstance(data, Connection.Message):
                    size = len(data)
                    if size > 1e9:
                        logging.warning("Data too big message not sended, size > 1e9")
                        continue

                    logging.info(f"Data sent: {data}")

                    writer.write(
                        f"DAT{len(str(size))}\r\n{size}\r\n\r\n{data}".encode("utf-8")
                    )
                else:
                    size = len(data)
                    if size > 1e9:
                        logging.warning("Data too big message not sended, size > 1e9")
                        continue

                    logging.info(f"Data sent: {data}")

                    if isinstance(data, str):
                        data = data.encode("utf-8")

                    writer.write(
                        f"RAW{len(str(size))}\r\n{size}\r\n\r\n".encode("utf-8") + data
                    )
            else:
                writer.write(b"PING")
            await writer.drain()

        writer.write(f"EXT{self.exitCode}".encode("utf-8"))
        await writer.drain()
        writer.close()
        return self.exitCode

    async def stop(self, code):
        """Stop the connection and send a exit signal
        Arguments:
            code {int} -- exit code must be between 0 and 9 (0 = success, 1-9 = error)

        Returns:
            None, make start function exits

        Raises:
            TypeError: if code is not an integer
            ValueError: if code is not between 0 and 9
        """
        if not isinstance(code, int):
            raise TypeError("Error: code must be an integer")
        if code < 0 or code > 9:
            raise ValueError("Error: code must be between 0 and 9")

        self.exitCode = code
        if code == 0:
            self.state = 1
        else:
            self.state = 2
