import numpy as np
from PIL import Image
import io
from .biochem_agent import BiochemAgent
from .ultrasound_agent import UltrasoundAgent
from .ct_mri_agent import CTMRIAgent
from .histo_agent import HistoAgent
from .histo_agent import HistoAgent
from .ct_lesion_agent import CTLesionAgent
from .prescription_agent import PrescriptionAgent
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RouterAgent:
    def __init__(self):
        self.biochem = BiochemAgent()
        self.ultrasound = UltrasoundAgent()
        self.ct_mri = CTMRIAgent()
        self.histo = HistoAgent()
        self.ct_lesion = CTLesionAgent()
        self.prescription = PrescriptionAgent()

    def route_and_predict(self, input_data, data_type="image", filename=""):
        """
        Main entry point.
        input_data: dict (for biochem) or bytes (for images)
        data_type: 'tabular' or 'image'
        """
        if data_type == "tabular":
            logging.info(f"Routing to Biochem Agent. Data: {input_data}")
            return self.biochem.predict(input_data)
        
        elif data_type == "image":
            # Heuristic routing based on image properties
            image_type = self._classify_image_type(input_data, filename)
            logging.info(f"Router detected image type: {image_type}")
            
            if image_type == "rx":
                logging.info("Routing to Prescription Agent...")
                rx_result = self.prescription.predict(input_data)
                
                # --- Multi-Agent Orchestration ---
                # Key Step: If the Prescription Agent extracted structured lab values,
                # pass them to the Biochem Agent for a health diagnosis.
                
                structured_labs = rx_result.get("labs_structured", {})
                # Heuristic: If we found at least a few relevant lab keys, run analysis
                if structured_labs and len(structured_labs) >= 1:
                     logging.info(f"Router: Found structured labs in Rx, chaining to Biochem Agent. Data: {structured_labs}")
                     biochem_result = self.biochem.predict(structured_labs)
                     
                     # Merge Results
                     # We want to keep the Rx details (medicines, text) but add the Biochem diagnosis
                     rx_result["diagnosis"] = biochem_result.get("diagnosis", "Unknown")
                     rx_result["biochem_analysis"] = biochem_result # Store full analysis if needed
                     
                     # Extend recommendations
                     if biochem_result.get("recommendations"):
                         rx_result["recommendations"] = (rx_result.get("recommendations") or []) + biochem_result.get("recommendations")
                         
                     # Add biochem confidence to details or average it? 
                     # For now, let's keep confidence as 1.0 (OCR success) or maybe partial?
                
                return rx_result

            elif image_type == "ultrasound":
                return self.ultrasound.predict(input_data)
            elif image_type == "ct":
                # Route specifically to the new CT Lesion Agent
                return self.ct_lesion.predict(input_data, filename=filename)
            elif image_type == "ct_mri":
                # Fallback for generic/MRI
                return self.ct_mri.predict(input_data)
            elif image_type == "histopathology":
                return self.histo.predict(input_data)
            else:
                return {"error": "Unknown image modality"}
        else:
            return {"error": "Unsupported data type"}

    def _classify_image_type(self, image_bytes, filename=""):
        # 1. Simple filename check (for demo reliability)
        fname = filename.lower()
        if "rx" in fname or "prescription" in fname or "report" in fname:
            return "rx"
        if "ultra" in fname or "us" in fname:
            return "ultrasound"
        if "ct" in fname or "volume" in fname:
            return "ct"
        if "mri" in fname:
            return "ct_mri"
        if "histo" in fname or "biopsy" in fname or "slide" in fname:
            return "histopathology"

        # 2. Content-based check (Fallback)
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_np = np.array(img)
            
            # Histopathology is typically Pink/Purple (Red/Blue channels high, Green variable/lower)
            # Ultrasound/CT/MRI are Grayscale (R~=G~=B)
            
            # Check saturation
            hsv_img = img.convert('HSV')
            s_channel = np.array(hsv_img)[:, :, 1]
            avg_saturation = np.mean(s_channel)
            
            if avg_saturation > 20: # Arbitrary threshold, H&E is colorful
                return "histopathology"
            
            # If Grayscale, distinguish Ultrasound vs CT/MRI
            # Ultrasound often has high noise / distinct fan shape (hard to detect simply)
            # For now, default to CT/MRI if grayscale, unless specific noise patterns found
            # (Simplification for demo)
            return "ct_mri" 
            
        except Exception as e:
            logging.error(f"Error in classification: {e}")
            return "unknown"
