import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import time
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "ultrasound_model.pth")
DUMMY_IMAGE_PATH = os.path.join(BASE_DIR, "test_data", "dummy_ultrasound.jpg")

# Hyperparameters
BATCH_SIZE: int = 4
LEARNING_RATE: float = 1e-4
EPOCHS: int = 3
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class DummyUltrasoundDataset(Dataset):
    def __init__(self, size: int = 100, transform=None):
        self.size = size
        self.transform = transform
        # Create dummy image if it doesn't exist (fallback)
        if not os.path.exists(DUMMY_IMAGE_PATH):
             img = Image.new('L', (224, 224), color=128)
             img.save(DUMMY_IMAGE_PATH)

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, idx):
        # Load the same dummy image/target for demonstration
        image = Image.open(DUMMY_IMAGE_PATH).convert('L')
        
        # Fake target class (0: Normal, 1: Fatty, 2: Tumor)
        target = torch.tensor(1) # Predict Fatty Liver for demo

        if self.transform:
            image = self.transform(image)

        return image, target

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=3):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 28 * 28, 128), # Assuming 224x224 input
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x

def train():
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    logging.info(f"Device: {DEVICE}")
    logging.info(f"Using dummy data from {DUMMY_IMAGE_PATH}")
    
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    
    dataset = DummyUltrasoundDataset(size=50, transform=transform) # Small dataset for fast demo
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = SimpleCNN(num_classes=3).to(DEVICE)
    
    # Resume Capabilities
    if os.path.exists(MODEL_SAVE_PATH):
        try:
            logging.info(f"Found existing model at {MODEL_SAVE_PATH}. Loading checkpoints...")
            state_dict = torch.load(MODEL_SAVE_PATH, map_location=DEVICE)
            model.load_state_dict(state_dict)
            logging.info("Model loaded successfully. Resuming training...")
        except Exception as e:
            logging.error(f"Failed to load existing model: {e}")
    else:
        logging.info("No existing model found. Starting fresh training.")

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()
    
    logging.info(f"Starting training for {EPOCHS} epochs...")
    model.train()
    
    for epoch in range(EPOCHS):
        for i, (images, targets) in enumerate(dataloader):
            images = images.to(DEVICE)
            targets = targets.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            if i % 5 == 0:
                logging.info(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i}/{len(dataloader)}], Loss: {loss.item():.4f}")
        
        # Save checkpoint
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        logging.info(f"Epoch {epoch+1} finished. Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
