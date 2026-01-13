import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class BiochemAgent:
    def __init__(self, model_path="models/biochem_model.pkl", scaler_path="models/biochem_scaler.pkl"):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        self._load_or_create_model()

    def _load_or_create_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            print(f"BiochemAgent: Loaded trained model from {self.model_path}")
            
            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                print(f"BiochemAgent: Loaded scaler from {self.scaler_path}")
        else:
            # Create a mock model for demo purposes if no trained model exists
            print("No trained model found. Creating a dummy Random Forest model.")
            self.model = RandomForestClassifier(n_estimators=100)
            # Train on dummy data
            X_dummy = np.random.rand(100, 10) # 10 features now
            y_dummy = np.random.randint(0, 2, 100)
            self.model.fit(X_dummy, y_dummy)

    def predict(self, data: dict):
        # 1. Feature Mapping: Frontend Keys -> Model Keys
        # Expected Model Order: Age, Gender, Total_Bilirubin, Direct_Bilirubin, 
        # Alkaline_Phosphotase, Alamine_Aminotransferase, Aspartate_Aminotransferase, 
        # Total_Protiens, Albumin, Albumin_and_Globulin_Ratio
        
        feature_map = {
            "Age": ["Age", "age"],
            "Gender": ["Gender", "sex", "gender"], # Needs encoding
            "Total_Bilirubin": ["Total_Bilirubin", "Bilirubin", "total_bilirubin"],
            "Direct_Bilirubin": ["Direct_Bilirubin", "Direct Bilirubin", "direct_bilirubin"],
            "Alkaline_Phosphotase": ["Alkaline_Phosphotase", "ALP", "alkaline_phosphatase"],
            "Alamine_Aminotransferase": ["Alamine_Aminotransferase", "ALT", "SGPT", "alamine_aminotransferase"],
            "Aspartate_Aminotransferase": ["Aspartate_Aminotransferase", "AST", "SGOT", "aspartate_aminotransferase"],
            "Total_Protiens": ["Total_Protiens", "Total Proteins", "Proteins", "total_proteins"], # Note typo in dataset 'Protiens'
            "Albumin": ["Albumin", "albumin"],
            "Albumin_and_Globulin_Ratio": ["Albumin_and_Globulin_Ratio", "A/G Ratio", "albumin_globulin_ratio"]
        }
        
        # Prepare input vector
        input_vector = []
        features_used_log = []
        
        # Helper to find value
        def get_val(keys, default=0.0):
            for k in keys:
                if k in data:
                    return data[k]
                # Check case insensitive
                for data_k in data.keys():
                    if data_k.lower() == k.lower():
                        return data[data_k]
            return default

        # Construct vector in correct order
        # Age
        input_vector.append(float(get_val(feature_map["Age"], 45))) # Default age 45
        
        # Gender (Male=1, Female=0)
        gender_val = get_val(feature_map["Gender"], "Male")
        if isinstance(gender_val, str):
             gender_code = 1 if gender_val.lower().startswith('m') else 0
        else:
             gender_code = int(gender_val)
        input_vector.append(gender_code)
        
        input_vector.append(float(get_val(feature_map["Total_Bilirubin"], 0.9)))
        input_vector.append(float(get_val(feature_map["Direct_Bilirubin"], 0.2)))
        input_vector.append(float(get_val(feature_map["Alkaline_Phosphotase"], 200)))
        input_vector.append(float(get_val(feature_map["Alamine_Aminotransferase"], 30)))
        input_vector.append(float(get_val(feature_map["Aspartate_Aminotransferase"], 30)))
        input_vector.append(float(get_val(feature_map["Total_Protiens"], 6.5)))
        input_vector.append(float(get_val(feature_map["Albumin"], 3.2)))
        input_vector.append(float(get_val(feature_map["Albumin_and_Globulin_Ratio"], 0.9)))
        
        try:
            # Convert to numpy array
            input_np = np.array(input_vector).reshape(1, -1)
            
            # Scale if scaler exists
            if self.scaler:
                 input_np = self.scaler.transform(input_np)
            
            prediction = self.model.predict(input_np)
            probs = self.model.predict_proba(input_np)
            
            class_id = int(prediction[0])
            confidence = float(np.max(probs))
            
            # Model was trained with: 1=Disease, 0=Healthy
            diagnosis_map = {0: "Healthy", 1: "Liver Disease Detected"}
            diagnosis = diagnosis_map.get(class_id, "Unknown")
            
            # Generate Recommendations
            recommendations = []
            if diagnosis == "Liver Disease Detected":
                recommendations = [
                    "Consult a Hepatologist immediately",
                    "Schedule a follow-up Elastography or Ultrasound",
                    "Avoid alcohol and hepatotoxic medications",
                    "Monitor liver enzymes (ALT/AST) weekly"
                ]
            elif diagnosis == "Healthy":
                recommendations = [
                    "Maintain a balanced diet and healthy weight",
                    "Regular annual checkups recommended",
                    "Vaccinate against Hepatitis A and B if not already done"
                ]
            else:
                 recommendations = ["Consult a general practitioner for interpretation"]

            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "recommendations": recommendations,
                "details": {
                    "probabilities": probs.tolist(), 
                    "features_used": list(feature_map.keys())
                }
            }

        except Exception as e:
            return {"error": str(e)}
