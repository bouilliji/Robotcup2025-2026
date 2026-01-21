from src.api.raspConnection import create_ports, Connection
import serial
import json
import time
import os

current_dir = os.path.dirname(__file__)
json_path = os.path.join(
    current_dir, "data", "test_api_data.json"
)  # Path for test data file

with open(json_path) as json_data:
    data = json.load(json_data)


def verif_port(port_path):
    """Verify if socat port is active"""
    try:
        seri = serial.Serial(port_path, timeout=0.1)  # Try to connect to the port
        seri.close()
        return True
    except (serial.SerialException, OSError):  # If port can't be accessed
        return False


message_received = ""  # Global var for the message received by conn2

proc = create_ports(
    "/tmp/ttyV12", "/tmp/ttyV13"
)  # Creation of the ports for the Connection

# Create the two Connection objects
conn1 = Connection("/tmp/ttyV12")
conn2 = Connection("/tmp/ttyV13")


# If a message with order test is received
@conn2.on("test")
def handler(data):
    global message_received
    message_received = data


def test_ports():
    port1 = data["port1"]
    port2 = data["port2"]

    proc_test = create_ports(port1, port2)  # Create ports

    # Verify if they are active
    assert verif_port(port1)
    assert verif_port(port2)

    proc_test.kill()  # Kill the process


def test_send_message():
    global proc
    global conn1
    global conn2
    global message_received

    # Start the Connection
    conn1.start()
    conn2.start()

    conn1.send("test", data["message"])  # Send a message to conn2 with conn1

    time.sleep(1)

    assert message_received == data["message"]  # Verify if message good

    # Stop connection
    conn1.stop(0)
    conn2.stop(0)

    proc.kill()  # Kill the process
