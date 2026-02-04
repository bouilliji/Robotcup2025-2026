import server, actuator_server, sensor_server
import logging
import time

if __name__ == "__main__":
    server.main()
    time.sleep(1)
    actuator_server.main()
    sensor_server.main()
    logging.info("Server starting...")