import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "ct_mri_model.pth")
DUMMY_IMAGE_PATH = os.path.join(BASE_DIR, "test_data", "dummy_ct.jpg") # Using CT dummy for generic

# Hyperparameters
BATCH_SIZE: int = 4
LEARNING_RATE: float = 1e-4
EPOCHS: int = 3
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class DummyCTMRIDataset(Dataset):
    def __init__(self, size: int = 50, transform=None):
        self.size = size
        self.transform = transform
        if not os.path.exists(DUMMY_IMAGE_PATH):
             img = Image.new('L', (256, 256), color=100)
             img.save(DUMMY_IMAGE_PATH)

    def __len__(self) -> int:
        return self.size

    def __getitem__(self, idx):
        image = Image.open(DUMMY_IMAGE_PATH).convert('L')
        # Target: 0 (HCC), 1 (Cirrhosis)
        target = torch.tensor(0) 

        if self.transform:
            image = self.transform(image)

        return image, target

class CTMRIModel(nn.Module):
    def __init__(self):
        super(CTMRIModel, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 2)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.conv(x)
        return self.fc(feat)

def train():
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    logging.info(f"Device: {DEVICE}")
    
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])
    
    dataset = DummyCTMRIDataset(size=50, transform=transform)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = CTMRIModel().to(DEVICE)
    
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
            
            if i % 10 == 0:
                logging.info(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i}/{len(dataloader)}], Loss: {loss.item():.4f}")
        
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        logging.info(f"Epoch {epoch+1} finished. Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
