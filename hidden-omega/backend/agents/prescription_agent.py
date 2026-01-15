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

    def _extract_lab_values(self, text_list):
        structured_labs = {}
        # Regex patterns for common liver labs
        # Matches: "ALT 45", "ALT: 45", "ALT-45", "Total Bilirubin 0.9", "S. Bilirubin (Total) 1.2"
        patterns = {
            "Alamine_Aminotransferase": [
                r"(?i)\b(?:alt|sgpt|alamine\s?aminotransferase)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)",
                r"(?i)\b(?:s\.?alt)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Aspartate_Aminotransferase": [
                r"(?i)\b(?:ast|sgot|aspartate\s?aminotransferase)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)",
                r"(?i)\b(?:s\.?ast)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Total_Bilirubin": [
                r"(?i)\b(?:total\s?bilirubin|t\.?\s?bil|bilirubin\s?\(?t(?:otal)?\)?)[\.\s]*[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)",
                r"(?i)\b(?:bil\.?\s?t)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Direct_Bilirubin": [
                r"(?i)\b(?:direct\s?bilirubin|d\.?\s?bil|bilirubin\s?\(?d(?:irect)?\)?)[\.\s]*[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)",
                r"(?i)\b(?:bil\.?\s?d)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Alkaline_Phosphotase": [
                r"(?i)\b(?:alp|alkaline\s?phosphotase|adkg)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)",
                r"(?i)\b(?:s\.?alp)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Albumin": [
                r"(?i)\b(?:albumin|alb|s\.?alb)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
            "Total_Protiens": [
                r"(?i)\b(?:total\s?proteins?|t\.?\s?proteins?|t\.?\s?prot)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ],
             "Albumin_and_Globulin_Ratio": [
                r"(?i)\b(?:a\/g\s?ratio|albumin\/globulin)[^:0-9\n]*[:\-\s]+([0-9]+\.?[0-9]*)"
            ]
        }

        full_text = " ".join(text_list)
        
        for canonical_key, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, full_text)
                if match:
                    try:
                        val = float(match.group(1))
                        structured_labs[canonical_key] = val
                        break 
                    except ValueError:
                        continue
        
        return structured_labs

    def _analyze_endoscopy(self, text_list):
        # Heuristics for Endoscopy Reports
        full_text = " ".join(text_list).lower()
        findings = []
        
        keywords = {
            "Esophagus": ["esophagus", "varices", "esophageal"],
            "Stomach": ["stomach", "gastritis", "ulcer", "fundus", "antrum"],
            "Duodenum": ["duodenum", "duodenal"],
            "Impression": ["impression", "conclusion", "diagnosis", "dx"]
        }
        
        for organ, keys in keywords.items():
            for k in keys:
                if k in full_text:
                    # simplistic: just note it was mentioned. 
                    # ideal: extraction of the line containing it.
                    findings.append(organ)
                    break
        
        return list(set(findings))

    def _generate_detailed_review(self, medicines, labs_structured, endoscopy_findings, suggestions):
        review = []
        
        if endoscopy_findings:
            review.append(f"**Procedure Report Detected**: likely Endoscopy/Gastroscopy.")
            review.append(f"Key structures mentioned: {', '.join(endoscopy_findings)}.")
            if "Esophagus" in endoscopy_findings and "Varices" in " ".join(endoscopy_findings): 
                 review.append("⚠️ Indication of Portal Hypertension (Varices).")

        if labs_structured:
            review.append(f"**Blood Panel Analysis**:")
            for k, v in labs_structured.items():
                review.append(f"- {k.replace('_', ' ')}: {v}")
            # Basic interp
            if labs_structured.get("Alamine_Aminotransferase", 0) > 40:
                review.append("⚠️ Elevated ALT indicates liver inflammation.")
        
        if medicines:
            review.append(f"**Medications Identified**: {len(medicines)} detected.")
        
        if not review:
            review.append("No specific clinical data extracted. Please ensure the image is clear and contains standard medical text.")
            
        return "\n".join(review)

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

            # Structured Extraction
            structured_labs = self._extract_lab_values(results)
            
            # Endoscopy Extraction
            endoscopy_findings = self._analyze_endoscopy(results)

            # Suggestions
            suggestions = self._get_suggestions(results)
            
            # Detailed Review
            detailed_review = self._generate_detailed_review(medicines, structured_labs, endoscopy_findings, suggestions)

            return {
                "type": "Prescription/Report Analysis",
                "medicines": medicines,
                "labs": labs,
                "labs_structured": structured_labs,
                "endoscopy_findings": endoscopy_findings, # New field
                "raw_text": results,
                "suggestions": suggestions,
                "diagnosis": "Report Analysis",
                "detailed_review": detailed_review, # New field
                "confidence": 1.0 
            }
        except Exception as e:
            return {"error": str(e)}
