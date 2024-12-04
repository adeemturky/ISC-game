from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import cv2
import numpy as np
import pytesseract
import torch

app = FastAPI()

# Load YOLO models
damage_model = YOLO('/Users/adoomy/Downloads/yolo11/runs/detect/train2/weights/best.pt')  # Replace with your YOLOv8 weights path
damage_class_names = damage_model.names  # Retrieve class names from the model
print("Damage Model Class Names:", damage_class_names)

yolov9_model_path = '/Users/adoomy/Downloads/yolo11/Automatic-number-plate-recognition-ANPR-with-Yolov9-and-EasyOCR/yolov9/runs/train/exp2/weights/best.pt'  # Replace with your YOLOv9 weights path
license_plate_model = torch.hub.load('WongKinYiu/yolov9', 'custom', path=yolov9_model_path)
license_plate_class_names = license_plate_model.names  # Retrieve class names from the model
print("License Plate Model Class Names:", license_plate_class_names)

@app.post("/analyze-image/")
async def analyze_image(file: UploadFile = File(...)):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")

    # Read image
    image_data = await file.read()
    image = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # Detect damages using YOLOv8
    damage_results = damage_model(image)
    damages = []
    if damage_results[0].boxes is not None:
        for result in damage_results[0].boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            confidence = float(result.conf[0])
            class_id = int(result.cls[0])
            class_name = damage_class_names.get(class_id, "Unknown")
            print(f"Detected damage - Class ID: {class_id}, Class Name: {class_name}, Confidence: {confidence}")
            damages.append({
                "bounding_box": [x1, y1, x2, y2],
                "confidence": confidence,
                "class_name": class_name
            })
    else:
        print("No damages detected.")

    # Detect license plates using YOLOv9
    license_plate_results = license_plate_model(image)
    license_plates = []
    if license_plate_results.xyxy[0] is not None and len(license_plate_results.xyxy[0]) > 0:
        for result in license_plate_results.xyxy[0]:
            x1, y1, x2, y2 = map(int, result[:4])
            conf = float(result[4])
            cls = int(result[5])
            class_name = license_plate_class_names.get(cls, "Unknown")
            print(f"Detected license plate - Class ID: {cls}, Class Name: {class_name}, Confidence: {conf}")
            # Extract license plate region
            license_plate_img = image[y1:y2, x1:x2]
            # Perform OCR
            license_text = pytesseract.image_to_string(license_plate_img, config='--psm 8')
            license_plates.append({
                "bounding_box": [x1, y1, x2, y2],
                "confidence": conf,
                "class_name": class_name,
                "license_text": license_text.strip()
            })
    else:
        print("No license plates detected.")

    return JSONResponse(content={
        "damages": damages,
        "license_plates": license_plates
    })
