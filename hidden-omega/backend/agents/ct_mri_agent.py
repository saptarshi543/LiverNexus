import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import io
import os

class CTMRIModel(nn.Module):
    def __init__(self):
        super(CTMRIModel, self).__init__()
        # Simulating a model that looks at texture/volume
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
            nn.Linear(64, 2) # Tumor vs Cirrhosis
        )

    def forward(self, x):
        feat = self.conv(x)
        return self.fc(feat)

class CTMRIAgent:
    def __init__(self, model_path="models/ct_mri_model.pth"):
        self.model = CTMRIModel()
        if os.path.exists(model_path):
             try:
                self.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
                print(f"CTMRIAgent: Loaded model from {model_path}")
             except Exception as e:
                print(f"CTMRIAgent: Failed to load model: {e}")
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

    def predict(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            tensor = self.transform(image).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
            
            # Simulated logic for demo
            pred_idx = torch.argmax(probs).item()
            classes = ["Hepatocellular Carcinoma", "Cirrhosis"]
            diagnosis = classes[pred_idx]
            confidence = probs[0][pred_idx].item()

            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "type": "CT/MRI Analysis",
                "details": {c: p.item() for c, p in zip(classes, probs[0])}
            }
        except Exception as e:
            return {"error": str(e)}
