from ultralytics import YOLO

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
                x1, y1, x2, y2 = xyxy
                area = max(0, x2 - x1) * max(0, y2 - y1)

                cars.append({
                    "label": label,
                    "confidence": round(conf, 4),
                    "bbox": [round(x, 2) for x in xyxy],
                    "area": round(area, 2)
                })

    # Sắp xếp xe theo diện tích giảm dần
    cars.sort(key=lambda x: x["area"], reverse=True)

    main_car = cars[0] if cars else None

    return {
        "detected": len(cars) > 0,
        "total_cars": len(cars),
        "main_car": main_car,
        "cars": cars
    }