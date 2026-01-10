import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
import numpy as np
import time

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "test_data", "liver_tumor")
IMAGES_DIR = os.path.join(DATA_DIR, "dataset_6", "dataset_6")
SUBSET_CSV_PATH = os.path.join(DATA_DIR, "lits_train_subset.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "ct_lesion_model_light.pth")

# Hyperparameters
BATCH_SIZE = 8
LEARNING_RATE = 1e-4
EPOCHS = 3 # Increased for better training
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class LiTSDataset(Dataset):
    def __init__(self, csv_file, root_dir, transform=None):
        self.data_frame = pd.read_csv(csv_file)
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        row = self.data_frame.iloc[idx]
        
        # Load Image
        img_name = os.path.basename(row['filepath'])
        img_path = os.path.join(self.root_dir, img_name)
        image = Image.open(img_path).convert('L') # Gray scale

        # Load Mask (Tumor)
        mask_name = os.path.basename(row['tumor_maskpath'])
        mask_path = os.path.join(self.root_dir, mask_name)
        mask = Image.open(mask_path).convert('L')

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)
            
            # Mask should be binary 0 or 1
            mask = (mask > 0).float()

        return image, mask

class LightweightUNet(nn.Module):
    def __init__(self):
        super(LightweightUNet, self).__init__()
        
        # Encoder
        self.enc1 = self.conv_block(1, 16)
        self.pool1 = nn.MaxPool2d(2)
        self.enc2 = self.conv_block(16, 32)
        self.pool2 = nn.MaxPool2d(2)
        self.enc3 = self.conv_block(32, 64)
        self.pool3 = nn.MaxPool2d(2)
        
        # Bottleneck
        self.bottleneck = self.conv_block(64, 128)
        
        # Decoder
        self.upconv3 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec3 = self.conv_block(128, 64)
        
        self.upconv2 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.dec2 = self.conv_block(64, 32)
        
        self.upconv1 = nn.ConvTranspose2d(32, 16, kernel_size=2, stride=2)
        self.dec1 = self.conv_block(32, 16)
        
        # Final
        self.final_conv = nn.Conv2d(16, 1, kernel_size=1) # Binary classification per pixel

    def conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        e1 = self.enc1(x)
        p1 = self.pool1(e1)
        
        e2 = self.enc2(p1)
        p2 = self.pool2(e2)
        
        e3 = self.enc3(p2)
        p3 = self.pool3(e3)
        
        b = self.bottleneck(p3)
        
        d3 = self.upconv3(b)
        # Pad if necessary (simple concatenation assuming 256x256 input)
        d3 = torch.cat((e3, d3), dim=1)
        d3 = self.dec3(d3)
        
        d2 = self.upconv2(d3)
        d2 = torch.cat((e2, d2), dim=1)
        d2 = self.dec2(d2)
        
        d1 = self.upconv1(d2)
        d1 = torch.cat((e1, d1), dim=1)
        d1 = self.dec1(d1)
        
        out = self.final_conv(d1)
        return out

def train():
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    print(f"Device: {DEVICE}")
    print(f"Loading data from {SUBSET_CSV_PATH}")
    
    # Transforms
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])
    
    dataset = LiTSDataset(SUBSET_CSV_PATH, IMAGES_DIR, transform=transform)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True if torch.cuda.is_available() else False)
    
    print(f"Dataset size: {len(dataset)}")
    
    model = LightweightUNet().to(DEVICE)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCEWithLogitsLoss() # Better numerical stability than BCELoss + Sigmoid
    
    print("Starting training...")
    model.train()
    
    start_time = time.time()
    
    for epoch in range(EPOCHS):
        running_loss = 0.0
        for i, (images, masks) in enumerate(dataloader):
            images = images.to(DEVICE)
            masks = masks.to(DEVICE)
            
            optimizer.zero_grad()
            
            outputs = model(images)
            loss = criterion(outputs, masks)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            if i % 100 == 0:
                print(f"Epoch [{epoch+1}/{EPOCHS}], Step [{i}/{len(dataloader)}], Loss: {loss.item():.4f}")
        
        # Save checkpoint at end of epoch
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        print(f"Epoch {epoch+1} finished. Model saved to {MODEL_SAVE_PATH}")

    end_time = time.time()
    print(f"Training finished in {end_time - start_time:.2f} seconds.")
    
    # Save Model (Final)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    train()
