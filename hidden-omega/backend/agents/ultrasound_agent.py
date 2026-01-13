import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io
import os

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
            nn.Linear(128 * 28 * 28, 128), # Assuming 224x224 input -> 28x28 after 3 pools
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class UltrasoundAgent:
    def __init__(self, model_path="models/ultrasound_model.pth"):
        self.model = SimpleCNN(num_classes=3) # Normal, Fatty, Tumor
        if os.path.exists(model_path):
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                print(f"UltrasoundAgent: Loaded model from {model_path}")
            except Exception as e:
                print(f"UltrasoundAgent: Failed to load model: {e}")
        self.model.eval() # Set to eval mode
        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        
        # Load weights if available, else random weights (Mock mode)

    def predict(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            tensor = self.transform(image).unsqueeze(0) # Batch dim
            
            with torch.no_grad():
                outputs = self.model(tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                
            pred_idx = torch.argmax(probs).item()
            confidence = probs[0][pred_idx].item()
            
            classes = ["Normal", "Fatty Liver", "Tumor"]
            diagnosis = classes[pred_idx]
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "type": "Ultrasound Analysis",
                "details": {c: p.item() for c, p in zip(classes, probs[0])}
            }
        except Exception as e:
            return {"error": str(e)}
