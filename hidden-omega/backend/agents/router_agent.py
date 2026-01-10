import numpy as np
from PIL import Image
import io
from .biochem_agent import BiochemAgent
from .ultrasound_agent import UltrasoundAgent
from .ct_mri_agent import CTMRIAgent
from .histo_agent import HistoAgent

class RouterAgent:
    def __init__(self):
        self.biochem = BiochemAgent()
        self.ultrasound = UltrasoundAgent()
        self.ct_mri = CTMRIAgent()
        self.histo = HistoAgent()

    def route_and_predict(self, input_data, data_type="image", filename=""):
        """
        Main entry point.
        input_data: dict (for biochem) or bytes (for images)
        data_type: 'tabular' or 'image'
        """
        if data_type == "tabular":
            print(f"Routing to Biochem Agent. Data: {input_data}")
            return self.biochem.predict(input_data)
        
        elif data_type == "image":
            # Heuristic routing based on image properties
            image_type = self._classify_image_type(input_data, filename)
            print(f"Router detected image type: {image_type}")
            
            if image_type == "ultrasound":
                return self.ultrasound.predict(input_data)
            elif image_type == "ct_mri":
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
        if "ultra" in fname or "us" in fname:
            return "ultrasound"
        if "ct" in fname or "mri" in fname:
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
            print(f"Error in classification: {e}")
            return "unknown"
