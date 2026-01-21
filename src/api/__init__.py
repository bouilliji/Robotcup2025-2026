import datetime
import logging

date = str(datetime.datetime.now()).replace(" ", "_").replace(":", ",")

# Config for logging
logging.basicConfig(
    filename=f"./../logs/{date}.log",  # Log file path
    filemode="w",
    datefmt="%d-%m %H:%M",
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    level=logging.INFO,  # Set to info level globally
)
