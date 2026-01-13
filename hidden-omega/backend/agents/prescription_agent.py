import easyocr
import numpy as np
from PIL import Image
import io
import json
import os
import re

class PrescriptionAgent:
    def __init__(self, med_db_path="data/liver_medications.json"):
        print("PrescriptionAgent: Loading EasyOCR Model...")
        # Load English model. gpu=False to be safe or True if available (user has torch, likely CPU based on previous output)
        self.reader = easyocr.Reader(['en'], gpu=False) 
        self.med_db_path = med_db_path
        self.med_db = self._load_med_db()

    def _load_med_db(self):
        if os.path.exists(self.med_db_path):
            with open(self.med_db_path, "r") as f:
                return json.load(f)
        return {"conditions": {}}

    def _is_medicine(self, text):
        # Heuristic keywords for meds
        keywords = ["mg", "ml", "tablet", "cap", "capsule", "syrup", "daily", "bd", "od", "tid", "po", "iv"]
        return any(k in text.lower() for k in keywords)

    def _is_lab(self, text):
        # Heuristic for lab values (numbers + common units or names)
        # Look for digits
        if not any(char.isdigit() for char in text):
            return False
        
        lab_keywords = ["g/dl", "iu/l", "mg/dl", "bilirubin", "alt", "ast", "sgpt", "sgot", "alp", "platelet", "inr"]
        return any(k in text.lower() for k in lab_keywords)

    def _get_suggestions(self, text_list):
        full_text = " ".join(text_list).lower()
        suggestions = []
        
        for condition, data in self.med_db.get("conditions", {}).items():
            # Check if any keyword key matches
            if any(k in full_text for k in data.get("keywords", [])):
                suggestions.append({
                    "condition": condition.replace("_", " ").title(),
                    "standard_care": data.get("medications", []),
                    "note": data.get("description", "")
                })
        
        if not suggestions:
            # Default fallback
            suggestions.append({
                "condition": "General Liver Support",
                "standard_care": ["Multivitamins", "Lifestyle Changes"],
                "note": "No specific condition detected. Consult specialist."
            })
            
        return suggestions

    def predict(self, image_bytes):
        try:
            # EasyOCR expects numpy array or file path
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            image_np = np.array(image)

            # Read text
            results = self.reader.readtext(image_np, detail=0) # detail=0 returns just text
            
            # Sort
            medicines = []
            labs = []
            unknown = []

            for line in results:
                if self._is_medicine(line):
                    medicines.append(line)
                elif self._is_lab(line):
                    labs.append(line)
                else:
                    unknown.append(line)

            # Suggestions
            suggestions = self._get_suggestions(results)

            return {
                "type": "Prescription Analysis",
                "medicines": medicines,
                "labs": labs,
                "raw_text": results,
                "suggestions": suggestions,
                "diagnosis": "Prescription Analysis", # For consistency with other agents
                "confidence": 1.0 # Placeholder
            }
        except Exception as e:
            return {"error": str(e)}
