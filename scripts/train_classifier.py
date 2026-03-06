from pathlib import Path
import copy
import json
import time

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models
from torch.utils.data import DataLoader

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "body_type"
MODEL_DIR = BASE_DIR / "models" / "classifier"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 16
NUM_WORKERS = 0
HEAD_EPOCHS = 4
FINETUNE_EPOCHS = 8

HEAD_LR = 1e-3
FINETUNE_LR = 1e-4

MODEL_PATH = MODEL_DIR / "body_type_resnet18.pth"
CLASS_MAP_PATH = MODEL_DIR / "body_type_classes.json"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

weights = models.ResNet18_Weights.DEFAULT
train_transform = weights.transforms()
eval_transform = weights.transforms()

train_dataset = datasets.ImageFolder(DATA_DIR / "train", transform=train_transform)
val_dataset = datasets.ImageFolder(DATA_DIR / "val", transform=eval_transform)
test_dataset = datasets.ImageFolder(DATA_DIR / "test", transform=eval_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS)

class_names = train_dataset.classes
num_classes = len(class_names)

print("Classes:", class_names)
print("Train size:", len(train_dataset))
print("Val size:", len(val_dataset))
print("Test size:", len(test_dataset))
print("Device:", DEVICE)

model = models.resnet18(weights=weights)
in_features = model.fc.in_features
model.fc = nn.Linear(in_features, num_classes)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()


def run_epoch(model, loader, criterion, optimizer=None):
    is_train = optimizer is not None
    model.train() if is_train else model.eval()

    running_loss = 0.0
    running_corrects = 0
    total = 0

    with torch.set_grad_enabled(is_train):
        for inputs, labels in loader:
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE)

            if is_train:
                optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)

            if is_train:
                loss.backward()
                optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels).item()
            total += labels.size(0)

    return running_loss / total, running_corrects / total


def train_phase(model, train_loader, val_loader, criterion, optimizer, epochs, phase_name):
    best_wts = copy.deepcopy(model.state_dict())
    best_val_acc = 0.0

    for epoch in range(epochs):
        print(f"\n[{phase_name}] Epoch {epoch + 1}/{epochs}")

        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion)

        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val   Loss: {val_loss:.4f} | Val   Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_wts = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_wts)
    return model, best_val_acc


start_time = time.time()

# Phase 1: freeze backbone, train head
for param in model.parameters():
    param.requires_grad = False
for param in model.fc.parameters():
    param.requires_grad = True

optimizer = optim.Adam(model.fc.parameters(), lr=HEAD_LR)
model, best_val_acc_phase1 = train_phase(
    model, train_loader, val_loader, criterion, optimizer, HEAD_EPOCHS, "HEAD"
)

print(f"\nBest Val Acc after HEAD phase: {best_val_acc_phase1:.4f}")

# Phase 2: unfreeze layer4 + fc
for param in model.layer4.parameters():
    param.requires_grad = True
for param in model.fc.parameters():
    param.requires_grad = True

optimizer = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=FINETUNE_LR
)
model, best_val_acc_phase2 = train_phase(
    model, train_loader, val_loader, criterion, optimizer, FINETUNE_EPOCHS, "FINETUNE"
)

print(f"\nBest Val Acc after FINETUNE phase: {best_val_acc_phase2:.4f}")

test_loss, test_acc = run_epoch(model, test_loader, criterion)
print(f"\nTest Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

torch.save(model.state_dict(), MODEL_PATH)
print(f"Saved model to: {MODEL_PATH}")

with open(CLASS_MAP_PATH, "w", encoding="utf-8") as f:
    json.dump(class_names, f, ensure_ascii=False, indent=2)

print(f"Saved class map to: {CLASS_MAP_PATH}")
print(f"Training complete in {time.time() - start_time:.2f} seconds")