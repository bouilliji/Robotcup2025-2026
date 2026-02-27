import server
import actuator_server
import line_server
import sensor_server

import logging
import time
import sensor_server
from api.raspConnection import Connection

if __name__ == "__main__":
    server.main()
    time.sleep(1)
    actuator_server.main()
    sensor_server.main()
<<<<<<< HEAD
    Robot = line_server.Robot()
    Robot.main()
=======
>>>>>>> e82de28 (Fix line sensor)



