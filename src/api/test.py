import raspConnection as conn
import threading
import time

connection = conn.Connection("/dev/pts/" + input("port number: "))

thread = threading.Thread(target=connection.start)
thread.daemon = True
thread.start()

@connection.on("bla")
def handler(data):
    print(data)
time.sleep(0.05)
try:
    while connection.isRunning():
        connection.send("bla",input("input bla: "))
except KeyboardInterrupt:
    connection.stop(0)
    time.sleep(0.5)