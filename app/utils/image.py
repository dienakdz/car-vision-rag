from pathlib import Path
from PIL import Image


def crop_image(image_path: str, bbox: list[float], output_path: str) -> dict:
    """
    Crop ảnh theo bbox [x1, y1, x2, y2] và lưu ra output_path.
    Trả về metadata của ảnh crop.
    """
    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    x1, y1, x2, y2 = bbox

    # Ép bbox về trong phạm vi ảnh
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(width, int(x2))
    y2 = min(height, int(y2))

    cropped = image.crop((x1, y1, x2, y2))

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_file)

    crop_width, crop_height = cropped.size

    return {
        "crop_path": str(output_file),
        "crop_width": crop_width,
        "crop_height": crop_height,
        "bbox_used": [x1, y1, x2, y2]
    }