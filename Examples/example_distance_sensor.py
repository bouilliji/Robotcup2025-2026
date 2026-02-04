import time
from Alphabot_librairy.DistanceSensor import DistanceSensor

DS = DistanceSensor()

try:
    while True:
        print(DS.get_distance())

        time.sleep(0.1)

except:
    print("fin")
