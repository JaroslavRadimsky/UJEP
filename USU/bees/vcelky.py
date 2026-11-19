import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, random_split
import torchvision.transforms as transforms
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import tensorflow_datasets as tfds
from torch.utils.tensorboard import SummaryWriter
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

writer = SummaryWriter("runs/bee_experiment")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load TFDS
ds_train = tfds.load('bee_dataset/bee_dataset_200', split='train')

# Dataset wrapper
class BeeDatasetTorch(Dataset):
    def __init__(self, tfds_dataset, transform=None):
        self.dataset = list(tfds_dataset)
        self.transform = transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        sample = self.dataset[idx]
        img = sample['input'].numpy()
        label = float(sample['output']['wasps_output'].numpy())
        label = torch.tensor(label, dtype=torch.float32)
        if self.transform:
            img = self.transform(img)
        return img, label

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((100, 200)),
    transforms.ToTensor()
])

full_dataset = BeeDatasetTorch(ds_train, transform=transform)
train_size = int(0.7 * len(full_dataset))
val_size = int(0.15 * len(full_dataset))
test_size = len(full_dataset) - train_size - val_size
train_set, val_set, test_set = random_split(full_dataset, [train_size, val_size, test_size])
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
val_loader = DataLoader(val_set, batch_size=32)
test_loader = DataLoader(test_set, batch_size=32)

# Model
class BeeCNN(nn.Module):
    def __init__(self):
        super(BeeCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.fc1 = nn.Linear(32 * 25 * 50, 128)
        self.fc2 = nn.Linear(128, 1)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 25 * 50)
        x = F.relu(self.fc1(x))
        x = torch.sigmoid(self.fc2(x)).squeeze(1)
        return x

# Evaluation
def evaluate_model(model, dataloader, threshold=0.5):
    model.eval()
    all_labels = []
    all_preds = []
    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            preds = (outputs > threshold).float()
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    return {
        'accuracy': accuracy_score(all_labels, all_preds),
        'precision': precision_score(all_labels, all_preds, zero_division=0),
        'recall': recall_score(all_labels, all_preds, zero_division=0),
        'f1': f1_score(all_labels, all_preds, zero_division=0),
    }

def print_classification_report(model, dataloader, threshold=0.5):
    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            preds = (outputs > threshold).float()
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=["bee", "wasp"]))


def plot_confusion_matrix(model, dataloader, threshold=0.5):
    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            preds = (outputs > threshold).float()
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    cm = confusion_matrix(all_labels, all_preds)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["bee", "wasp"], yticklabels=["bee", "wasp"])
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.show()


# Load or initialize model
checkpoint_path = "checkpoint.pth"
start_epoch = 0
best_f1 = 0.0
model = BeeCNN().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.BCELoss()

if os.path.exists(checkpoint_path):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch'] + 1
    best_f1 = checkpoint['best_f1']
    print(f"Resuming training from epoch {start_epoch}, best F1 so far: {best_f1:.4f}")
else:
    print("Starting training from scratch.")

# Training loop
num_epochs = 10
for epoch in range(start_epoch, num_epochs):
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    metrics = evaluate_model(model, val_loader)
    writer.add_scalar('Loss/train', running_loss / len(train_loader), epoch)
    writer.add_scalar('F1', metrics['f1'], epoch)


    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'best_f1': max(best_f1, metrics['f1'])  # update best if needed
    }, checkpoint_path)

    print(f"\nEpoch {epoch+1} Summary")
    print(f"Train Loss: {running_loss / len(train_loader):.4f}")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

# Final evaluation on test set
model.eval()
test_metrics = evaluate_model(model, test_loader)
print("\nFinal test set performance:")
for k, v in test_metrics.items():
    print(f"{k}: {v:.4f}")


print_classification_report(model, test_loader)
plot_confusion_matrix(model, test_loader)