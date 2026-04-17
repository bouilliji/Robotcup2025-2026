from picamera2 import Picamera2


class Camera:
    def __init__(self):
        self.camera = Picamera2()
        self.camera.start()

    def frame(self):
        return self.camera.capture_image()

    def save(self, path="img.jpg"):
        self.frame().save(path)


if __name__ == "__main__":
    import time

    cam = Camera()
    while True:
        time.sleep(0.5)
        cam.save()
