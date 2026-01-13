from agents.prescription_agent import PrescriptionAgent
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np

def create_dummy_image():
    # Create white image with text
    img = Image.new('RGB', (400, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    # Add some text acting as prescription
    d.text((10, 10), "Rx", fill=(0, 0, 0))
    d.text((10, 50), "Amoxicillin 500mg daily", fill=(0, 0, 0))
    d.text((10, 80), "ALT 45 IU/L", fill=(0, 0, 0))
    d.text((10, 110), "Viral Hepatitis", fill=(0, 0, 0))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    print("Initializing Agent...")
    agent = PrescriptionAgent()
    print("Agent Initialized.")
    
    print("Creating Dummy Image...")
    img_bytes = create_dummy_image()
    
    print("Running Prediction...")
    result = agent.predict(img_bytes)
    print("Prediction Result:", result)
    print("Done.")
