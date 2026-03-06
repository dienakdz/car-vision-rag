from pathlib import Path
import json

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms, models
import torch.nn as nn

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "models" / "classifier"

MODEL_PATH = MODEL_DIR / "body_type_resnet18.pth"
CLASS_MAP_PATH = MODEL_DIR / "body_type_classes.json"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

IMAGE_SIZE = 224

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

model = None
class_names = None


def load_classifier():
    global model, class_names

    if model is not None and class_names is not None:
        return model, class_names

    if not MODEL_PATH.exists() or not CLASS_MAP_PATH.exists():
        return None, None

    with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
        class_names = json.load(f)

    weights = models.ResNet18_Weights.DEFAULT
    loaded_model = models.resnet18(weights=weights)
    in_features = loaded_model.fc.in_features
    loaded_model.fc = nn.Linear(in_features, len(class_names))
    loaded_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    loaded_model.to(DEVICE)
    loaded_model.eval()

    model = loaded_model
    return model, class_names


def build_confidence_message(confidence: float) -> str:
    if confidence >= 0.7:
        return "Phân loại body type thành công với độ tin cậy khá cao."
    elif confidence >= 0.5:
        return "Phân loại body type thành công, nhưng độ tin cậy ở mức trung bình."
    else:
        return "Model đã đưa ra dự đoán, nhưng độ tin cậy còn thấp. Nên xem thêm top_k."


def classify_body_type(crop_image_path: str) -> dict:
    model, class_names = load_classifier()

    if model is None or class_names is None:
        return {
            "predicted_label": None,
            "confidence": None,
            "top_k": [],
            "is_uncertain": True,
            "message": "Chưa có model body type đã train."
        }

    image = Image.open(crop_image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)[0]

    top_probs, top_indices = torch.topk(probs, k=min(3, len(class_names)))

    top_k = []
    for score, idx in zip(top_probs, top_indices):
        top_k.append({
            "label": class_names[idx.item()],
            "score": round(score.item(), 4)
        })

    confidence = round(top_k[0]["score"], 4)
    predicted_label = top_k[0]["label"]
    is_uncertain = confidence < 0.5

    return {
        "predicted_label": predicted_label,
        "confidence": confidence,
        "top_k": top_k,
        "is_uncertain": is_uncertain,
        "message": build_confidence_message(confidence)
    }