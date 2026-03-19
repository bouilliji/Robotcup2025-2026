import server
import actuator_server
import line_server
import sensor_server
import time


if __name__ == "__main__":
    server.main()
    time.sleep(1)
    actuator_server.main()
    sensor_server.main()
    Robot = line_server.Robot()
    Robot.main()

    def stop():
        actuator_server.stop()
        Robot.stop()
        sensor_server.stop()
        server.stop()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop()
