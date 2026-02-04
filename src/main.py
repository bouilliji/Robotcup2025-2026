import server
import actuator_server
import sensor_server
import logging
import time
from api.raspConnection import Connection

conn = Connection("/tmp/ttyV7")

if __name__ == "__main__":
    server.main()
    time.sleep(1)
    actuator_server.main()
    sensor_server.main()

    logging.info("Server starting...")

    conn.start()

    conn.send("motorWhile", {"left": 100, "right": 100, "time": 10})

    conn.stop(0)
