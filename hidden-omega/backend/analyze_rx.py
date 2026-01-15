from agents.prescription_agent import PrescriptionAgent
import os
import sys

# Add directory to path to handle imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IMAGES = [
    r"../test_data/Prescription/prescriptionImg.jpg",
    r"../test_data/Prescription/prescriptionImg2.jpg",
    r"../test_data/Prescription/prescriptionImg3.jpg"
]

if __name__ == "__main__":
    print("Initializing Agent...")
    try:
        agent = PrescriptionAgent()
    except Exception as e:
        print(f"Failed to init agent: {e}")
        exit(1)
    
    for img_path in IMAGES:
        print(f"\n\n==========================================")
        print(f"Processing {os.path.basename(img_path)}...")
        if not os.path.exists(img_path):
            print(f"Error: Image not found at {img_path}")
            continue

        try:
            with open(img_path, "rb") as f:
                image_bytes = f.read()
            
            result = agent.predict(image_bytes)
            print("--- Analysis ---")
            print(f"Structured Labs: {result.get('labs_structured')}")
            print("\nRaw Text Snippet (All Lines):")
            for i, line in enumerate(result.get('raw_text')):
                print(f"{i}: {line}") 
        except Exception as e:
            print(f"Error: {e}")
