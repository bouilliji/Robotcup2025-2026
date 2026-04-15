import cv2
from time import sleep
from picamera2 import Picamera2

from ultralytics import YOLO
import threading


class Cam:
    def __init__(self):
        self.model = YOLO(r"/home/athena/dev/Robotcup2025-2026/Examples/last.onnx")

        self.cam = Picamera2()
        self.cam.start()

        self.frame = cv2.imread("img.png")

        analyse = threading.Thread(target=self.thread, daemon=True)
        analyse.start()

        self.analyse_yolo()

    def dist_milieu(self, x1, x2):
        mid = (x1 + x2) / 2
        return mid - 320

    def read_result(self):
        self.object = []
        result = self.results[0]

        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls)
            label = self.model.names[cls_id]
            conf = float(box.conf)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            if cls_id == 0:
                self.object.insert(
                    0, {"width": abs(y2 - y1), "mid_dist": self.dist_milieu(x1, x2)}
                )
            else:
                self.object.append(
                    {"width": abs(y2 - y1), "mid_dist": self.dist_milieu(x1, x2)}
                )

    def go_to_ball(self):
        if len(self.object) == 0:
            return

        ball = self.object[0]
        mid = ball["mid_dist"]
        width = ball["width"]
        if mid > 20:
            print("Droite")
        elif mid < -20:
            print("Gauche")
        else:
            print("Mid")

    def cam_reader(self):
        while True:
            pict = self.cam.capture_array()

            cv2.imwrite("img.png", pict)
            self.frame = cv2.imread("img.png")

    def while_yolo(self):
        while True:
            self.analyse_yolo()
            print("thread yolo")

    def analyse_yolo(self):
        self.results = self.model.predict(self.frame, verbose=False)
        print("analyse yolo")

    def thread(self):
        while True:
            pict = self.cam.capture_array()

            cv2.imwrite("img.png", pict)
            self.frame = cv2.imread("img.png")

            self.results = self.model.predict(self.frame, verbose=False)
            print("analyse yolo")

    def main(self):
        while True:
            self.read_result()
            self.go_to_ball()
            sleep(0.5)


cam = Cam()
cam.main()
