from pathlib import Path
import random
import shutil

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = BASE_DIR / "data" / "raw" / "body_type_source"
TARGET_DIR = BASE_DIR / "data" / "raw" / "body_type"

TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

MAX_IMAGES_PER_CLASS = 600
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

def clear_target_dirs():
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

def split_files(files):
    random.shuffle(files)
    total = len(files)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train_files = files[:train_end]
    val_files = files[train_end:val_end]
    test_files = files[val_end:]

    return train_files, val_files, test_files


def copy_files(file_list, split_name, class_name):
    split_class_dir = TARGET_DIR / split_name / class_name
    split_class_dir.mkdir(parents=True, exist_ok=True)

    for idx, file_path in enumerate(file_list):
        new_name = f"{class_name}_{idx:05d}{file_path.suffix.lower()}"
        shutil.copy2(file_path, split_class_dir / new_name)


def main():
    clear_target_dirs()

    class_dirs = [d for d in SOURCE_DIR.iterdir() if d.is_dir()]

    for class_dir in class_dirs:
        raw_class_name = class_dir.name
        class_name = raw_class_name

        files = [
            f for f in class_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]

        if not files:
            print(f"[WARNING] No images found in class: {raw_class_name}")
            continue

        random.shuffle(files)
        files = files[:MAX_IMAGES_PER_CLASS]

        train_files, val_files, test_files = split_files(files)

        copy_files(train_files, "train", class_name)
        copy_files(val_files, "val", class_name)
        copy_files(test_files, "test", class_name)

        print(f"\nRaw class: {raw_class_name} -> Normalized: {class_name}")
        print(f"  Used total: {len(files)}")
        print(f"  Train: {len(train_files)}")
        print(f"  Val:   {len(val_files)}")
        print(f"  Test:  {len(test_files)}")

    print("\nDone splitting dataset.")


if __name__ == "__main__":
    main()