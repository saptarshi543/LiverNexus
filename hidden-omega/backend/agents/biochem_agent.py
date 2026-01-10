import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class BiochemAgent:
    def __init__(self, model_path="models/biochem_model.pkl"):
        self.model_path = model_path
        self.model = None
        self._load_or_create_model()

    def _load_or_create_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            # Create a mock model for demo purposes if no trained model exists
            print("No trained model found. Creating a dummy Random Forest model.")
            self.model = RandomForestClassifier(n_estimators=100)
            # Train on dummy data
            X_dummy = np.random.rand(100, 5) # 5 common LFT parameters
            y_dummy = np.random.randint(0, 2, 100)
            self.model.fit(X_dummy, y_dummy)

    def predict(self, data: dict):
        # Expecting keys: ALT, AST, ALP, Albumin, Bilirubin
        df = pd.DataFrame([data])
        # Ensure correct order/columns (in a real app, logic would be stricter)
        # For demo, just taking values
        try:
            prediction = self.model.predict(df.values)
            probs = self.model.predict_proba(df.values)
            class_id = int(prediction[0])
            confidence = float(np.max(probs))
            
            diagnosis_map = {0: "Healthy", 1: "Liver Disease Detected"}
            diagnosis = diagnosis_map.get(class_id, "Unknown")
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "details": {"probabilities": probs.tolist()}
            }
        except Exception as e:
            return {"error": str(e)}
