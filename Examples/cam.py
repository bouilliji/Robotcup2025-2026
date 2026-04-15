import picamera2
import cv2
import PIL

cam = picamera2.Picamera2()
cam.start()

pict = cam.capture_image()
pict.save("img.jpg")
# open("logging.out","w").write(str(pict))
# open("logging.out","a").write("\n\n"+str(frame))
