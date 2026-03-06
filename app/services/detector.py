from ultralytics import YOLO

# Model sẽ tự tải ở lần chạy đầu tiên nếu chưa có
model = YOLO("yolo11n.pt")


def detect_car(image_path: str) -> dict:
    results = model(image_path)

    cars = []

    for r in results:
        names = r.names

        if r.boxes is None:
            continue

        for box in r.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            label = names[cls_id]

            if label == "car":
                xyxy = box.xyxy[0].tolist()
                cars.append({
                    "label": label,
                    "confidence": round(conf, 4),
                    "bbox": [round(x, 2) for x in xyxy]
                })

    return {
        "detected": len(cars) > 0,
        "total_cars": len(cars),
        "cars": cars
    }