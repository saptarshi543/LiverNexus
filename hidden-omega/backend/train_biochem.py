import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# 1. Load Data
DATA_PATH = "../test_data/ILPD/indian_liver_patient.csv"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "biochem_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "biochem_scaler.pkl")

def train():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        return

    print("Loading ILPD dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # 2. Preprocessing
    # Gender Encoding: Male=1, Female=0
    df['Gender'] = df['Gender'].apply(lambda x: 1 if x == 'Male' else 0)
    
    # Handle Missing Values in 'Albumin_and_Globulin_Ratio'
    df['Albumin_and_Globulin_Ratio'] = df['Albumin_and_Globulin_Ratio'].fillna(df['Albumin_and_Globulin_Ratio'].mean())
    
    # Target Encoding: Dataset (1=Disease, 2=Healthy) -> (1=Disease, 0=Healthy)
    # The original dataset uses 2 for healthy, we want 0 for healthy to match standard binary classification
    df['Dataset'] = df['Dataset'].map({1: 1, 2: 0})
    
    print(f"Data Shape: {df.shape}")
    print(f"Class Distribution:\n{df['Dataset'].value_counts()}")

    # Features and Target
    X = df.drop('Dataset', axis=1)
    y = df['Dataset']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scaling (Good practice for some models, though RF is robust, consistent input handling is better)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 3. Train Model
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # 4. Evaluate
    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # 5. Save Artifacts
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    
    with open(SCALER_PATH, 'wb') as f:
        pickle.dump(scaler, f)
        
    print(f"Model saved to {MODEL_PATH}")
    print(f"Scaler saved to {SCALER_PATH}")
    print("Training Complete.")

if __name__ == "__main__":
    train()
