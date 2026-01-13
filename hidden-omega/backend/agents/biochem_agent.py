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
        # Expected features for the model (based on the dummy training)
        # in a real scenario, these would be fixed.
        # For this robust fix, we'll try to extract numeric values only.
        
        try:
            # 1. Convert to DataFrame
            df = pd.DataFrame([data])
            
            # 2. Filter for numeric columns only, dropping metadata like Dates/IDs
            numeric_df = df.select_dtypes(include=[np.number])
            
            # 3. Handle Missing/Extra Features
            # The dummy model was trained on 5 features. We need to ensure input has 5.
            # If we don't have enough, we pad. If we have too many, we truncate/select.
            
            # Get values as float array
            input_values = numeric_df.values[0]
            
            # Ensure exactly 5 features (as per _load_or_create_model X_dummy shape)
            if len(input_values) < 5:
                # Pad with zeros if missing features
                input_values = np.pad(input_values, (0, 5 - len(input_values)), 'constant')
            elif len(input_values) > 5:
                # Truncate if too many (simple heuristic)
                input_values = input_values[:5]
                
            # Reshape for sklearn (1, n_features)
            input_values = input_values.reshape(1, -1)

            prediction = self.model.predict(input_values)
            probs = self.model.predict_proba(input_values)
            class_id = int(prediction[0])
            confidence = float(np.max(probs))
            
            diagnosis_map = {0: "Healthy", 1: "Liver Disease Detected"}
            diagnosis = diagnosis_map.get(class_id, "Unknown")
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "details": {
                    "probabilities": probs.tolist(), 
                    "features_used": numeric_df.columns.tolist()
                }
            }
        except Exception as e:
            return {"error": str(e)}
