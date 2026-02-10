import server
import actuator_server
import logging
import time
from api.raspConnection import Connection

conn = Connection("/tmp/ttyV7", "SL -> server")

if __name__ == "__main__":
    server.main()
    time.sleep(1)
    actuator_server.main()
    # sensor_server.main()

    logging.info("Server SL starting...")

    conn.start()

    time.sleep(2)

    conn.send("motorWhile", {"left": -100, "right": -100, "time": 10})

    time.sleep(1)

    conn.stop(0)
