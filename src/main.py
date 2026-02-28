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
