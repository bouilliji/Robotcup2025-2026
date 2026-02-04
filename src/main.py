import server, actuator_server, sensor_server
import logging

if __name__ == "__main__":
    server.main()
    actuator_server
    sensor_server.main()
    logging.info("Server starting...")