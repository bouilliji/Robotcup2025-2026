import sys

sys.path.insert(0, "../src/")

# Importing required module
from api.raspConnection import create_ports, Connection
from serial.tools import list_ports
import time

# Using system() method to
# execute shell commands
proc = create_ports("/tmp/ttyV0", "/tmp/ttyV1")

time.sleep(20)


available_ports = list_ports.comports()
print(f"available ports: {[x.device for x in available_ports]}")

proc.kill()
