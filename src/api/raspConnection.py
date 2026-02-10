import json
import logging
import serial
import threading
import time
import subprocess

# Create handler to show log
console = logging.StreamHandler()

logging.getLogger("").setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

new_id = 0


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

    def __init__(self, port: str, name: str = None):
        """Create a new connection
        Arguments:
            port {str} -- port to connect to
        Raises:
            TypeError: if either port is not a string or dbLevel is not a DebugLevel
        """
        global new_id

        def _defaultRaw(_):
            logging.warning(f"Connection {self.name} : No handler for raw data")

        def _defaultMessage(ordre: str, _):
            logging.warning(
                f"Connection {self.name} : No handler for ordre {ordre} and no default handler"
            )

        self.id = new_id
        self.port = port
        self.toSend = []
        self.state = 1  # 0 = running, 1 = stopped, 2 = error
        self.exitCode = 0

        # functions to call when data is received
        self.onRaw = _defaultRaw
        self.onMessage = _defaultMessage
        self.handlers = dict()

        if name is not None:
            self.name = name + " " * (20 - len(name))
        else:
            self.name = self.id

        new_id += 1

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

    def send(self, ordre: str, data) -> None:  # used to send ordonated data
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

        logging.info(f"Connection {self.name} : send {ordre}")

    def sendRaw(self, data) -> None:
        """Send raw data to the raspberry pi
        Arguments:
            data {bytes} -- data to send
        Raises:
            TypeError: if data is not bytes
        """
        if not isinstance(data, bytes):
            raise TypeError("Error: raw data must be bytes")
        self.toSend.append(data)

        logging.info(f"Connection {self.name} : send raw data")

    def isRunning(self) -> bool:
        """Verify if the connection is still running
        Returns:
            bool -- True if the connection is still running
        """
        return self.state == 0

    def isLate(self) -> bool:  # to many messages are in the queue
        """Verify if there is too many messages in the queue
        Returns:
            bool -- True if there is too many messages in the queue
        """
        return len(self.toSend) > 10

    def start(self, baudrate: int = 115200) -> int:
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

        logging.info(f"Connection {self.name} : Starting...")

        # open serial connection
        seri = serial.Serial(self.port, baudrate)
        self.state = 0

        # send first ping
        seri.write(b"PING")
        seri.flush()

        def listen_for_data():
            while self.isRunning():
                if seri.in_waiting != 0:
                    data = seri.read(4)  # header of packet /in {DAT0, RAW0, PING, EXT0}
                    logging.info(f"Connection {self.name} : Packet received: {data}")

                    # handling incoming packet
                    if data == b"PING":
                        pass
                    elif data[:3] == b"DAT":
                        # read data
                        size = int(seri.read(int(data[3:]) + 6))
                        data = str(seri.read(size))
                        ordre, donnee = data[2 : len(data) - 1].split("\\r\\n")

                        logging.info(
                            f"Connection {self.name} : Data received: {ordre}\r\n{donnee}"
                        )

                        # call the right handler function
                        if ordre in self.handlers:
                            handler_thread = threading.Thread(
                                target=self.handlers[ordre], args=(json.loads(donnee),)
                            )
                            handler_thread.daemon = True  # Make thread a daemon so it won't block program exit
                            handler_thread.start()
                        else:
                            # Default handler for messages
                            handler_thread = threading.Thread(
                                target=self.onMessage, args=(ordre, json.loads(donnee))
                            )
                            handler_thread.daemon = True
                            handler_thread.start()
                    elif data[:3] == b"RAW":
                        size = int(seri.read(int(data[3:]) + 6))
                        data = seri.read(size)

                        logging.info(
                            f"Connection {self.name} : Raw data received: \r\n{data}"
                        )

                        # Handle raw data in a separate thread
                        handler_thread = threading.Thread(
                            target=self.onRaw, args=(data,)
                        )
                        handler_thread.daemon = True
                        handler_thread.start()

                    elif data[:3] == b"EXT":
                        logging.info(
                            f"Connection {self.name} : Exited with code: {data[3:]}"
                        )

                        self.state = (data[3:] == b"0") + 1
                        return int(str(data[3:]))
                    else:
                        logging.error(
                            f"Connection {self.name} : Received an unknown header: {data}"
                        )

                    # handling response
                    if len(self.toSend) > 0:
                        data = self.toSend.pop(0)
                        if isinstance(data, Connection.Message):
                            size = len(data)
                            if size > 1e9:
                                logging.warning(
                                    f"Connection {self.name} : Data too big, message not sent, size > 1e9"
                                )
                                continue

                            logging.info(f"Connection {self.name} : Data sent: {data}")
                            seri.write(
                                f"DAT{len(str(size))}\r\n{size}\r\n\r\n{data}".encode(
                                    "utf-8"
                                )
                            )
                        else:
                            size = len(data)
                            if size > 1e9:
                                logging.warning(
                                    f"Connection {self.name} : Data too big, message not sent, size > 1e9"
                                )
                                continue

                            logging.info(f"Connection {self.name} : Data sent: {data}")

                            if isinstance(data, str):
                                data = data.encode("utf-8")

                            seri.write(
                                f"RAW{len(str(size))}\r\n{size}\r\n\r\n".encode("utf-8")
                                + data
                            )
                    else:
                        seri.write(b"PING")
                    seri.flush()
                else:
                    logging.warning(f"Connection {self.name} : No response")
                    time.sleep(0.1)

                time.sleep(0.1)

        # Create a thread for listening to incoming data
        listener_thread = threading.Thread(target=listen_for_data)
        listener_thread.start()

        logging.info(f"Connection {self.name} : Started !")

        return self.exitCode

    def stop(self, code):
        """Stop the connection and send an exit signal
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

        logging.info(f"Connection {self.name} : Stopping...")

        self.exitCode = code
        if code == 0:
            self.state = 1
        else:
            self.state = 2


def create_ports(port1: str, port2: str) -> subprocess.Popen:
    """Create virtual ports with socat
    Arguments:
        port1 {str} -- port1 need to be "/tmp/ttyVX" with X a number not already used
        port2 {str} -- port2 need to be "/tmp/ttyVX" with X a number not already used

    Returns:
        process of socat command

    Raises:
        None
    """

    # Command to create ports with socat
    proc = subprocess.Popen(
        f"socat -d -d PTY,link={port1},raw,echo=0 PTY,link={port2},raw,echo=0",
        shell=True,
    )

    time.sleep(2)  # Wait for creation of the ports

    logging.info(f"Ports {port1} and {port2} created")

    return proc  # Return the process
