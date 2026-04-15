from ultralytics import YOLO

model = YOLO("last6.pt")
model.export(format="onnx", dynamic=True)
