from ultralytics import YOLO
import cv2

model = YOLO("path to Model")


while True:
    results = model.predict(source="0", conf=0.5, verbose=False)

    for res in results:
        box = res.boxes
        cls = box.cls
        xywh = box.xywh
        for i in range(len(cls)):  # pour tout les object detected
            iden = cls[i].item()
            donner_pos = xywh[i].tolist()
            cord = (donner_pos[0], donner_pos[1])  # pos x et y de l'objet
