import RPi.GPIO as GPIO
import time
import subprocess
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

process = None
mode = "line"

LONG_PRESS_TIME = 1.5
DOUBLE_CLICK_TIME = 0.4

last_click_time = 0
press_start_time = 0
click_count = 0


def start_robot():
    global process, mode
    print(f"STARTING ROBOT in {mode} mode")
    process = subprocess.Popen([sys.executable, "main.py", "--mode", mode], cwd="./src")


def stop_robot():
    global process
    if process:
        print("STOPPING ROBOT")
        process.terminate()
        process.wait()
        process = None


def toggle_robot():
    global process
    if process is None:
        start_robot()
    else:
        stop_robot()


def switch_mode_and_restart():
    global mode
    mode = "arena" if mode == "line" else "line"
    print(f"SWITCH MODE -> {mode}")

    stop_robot()
    start_robot()


try:
    while True:
        if GPIO.input(17) == 1:
            press_start_time = time.time()

            # attendre relâchement
            while GPIO.input(17) == 1:
                time.sleep(0.01)

            press_duration = time.time() - press_start_time

            # APPUI LONG
            if press_duration >= LONG_PRESS_TIME:
                toggle_robot()
                click_count = 0

            else:
                # CLICK COURT
                current_time = time.time()

                if current_time - last_click_time <= DOUBLE_CLICK_TIME:
                    click_count += 1
                else:
                    click_count = 1

                last_click_time = current_time

                if click_count == 2:
                    switch_mode_and_restart()
                    click_count = 0

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nArrêt du programme par l'utilisateur.")

finally:
    stop_robot()
    GPIO.cleanup()
