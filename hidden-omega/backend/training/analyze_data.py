import pandas as pd
import os
import numpy as np
from PIL import Image

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # hidden-omega
DATA_DIR = os.path.join(BASE_DIR, "test_data", "liver_tumor")
IMAGES_DIR = os.path.join(DATA_DIR, "dataset_6", "dataset_6")
CSV_PATH = os.path.join(DATA_DIR, "lits_train.csv")
SUBSET_CSV_PATH = os.path.join(DATA_DIR, "lits_train_subset.csv")
SAMPLE_RATE = 0.3

def fix_path(path):
    # CSV paths are like: ../input/lits-png/dataset_6/volume-2_0.png
    # We need just the filename: volume-2_0.png
    return os.path.basename(path)

def main():
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Total rows: {len(df)}")

    # Fix paths
    print("Fixing paths and verifying files...")
    valid_rows = []
    
    # We will verify a few files to ensure the directory is correct
    # listing directory once is faster than OS.path.exists for every file if directory is huge
    # checking file existence
    
    available_files = set(os.listdir(IMAGES_DIR))
    
    missing_count = 0
    total_files = len(df)
    for idx, row in df.iterrows():
        if idx % 1000 == 0:
            print(f"Verified {idx}/{total_files}...")

        img_name = fix_path(row['filepath'])
        mask_name = fix_path(row['tumor_maskpath']) # Using tumor mask path
        liver_mask_name = fix_path(row['liver_maskpath'])
        
        if img_name in available_files and mask_name in available_files and liver_mask_name in available_files:
            # Update path to absolute path for easier loading later
            row['filepath'] = os.path.join(IMAGES_DIR, img_name)
            row['tumor_maskpath'] = os.path.join(IMAGES_DIR, mask_name)
            row['liver_maskpath'] = os.path.join(IMAGES_DIR, liver_mask_name)
            valid_rows.append(row)
        else:
            missing_count += 1
            if missing_count < 5:
                print(f"Missing file: {img_name}")

    print(f"Verified {len(valid_rows)}/{len(df)} rows. Missing: {missing_count}")
    
    valid_df = pd.DataFrame(valid_rows)
    
    # Sampling
    print(f"Sampling {SAMPLE_RATE*100}% of data...")
    subset_df = valid_df.sample(frac=SAMPLE_RATE, random_state=42)
    print(f"Subset size: {len(subset_df)}")
    
    # Save subset
    subset_df.to_csv(SUBSET_CSV_PATH, index=False)
    print(f"Saved subset to {SUBSET_CSV_PATH}")

    # Basic Stats
    print("Calculating positive/negative statistics on subset...")
    positives = subset_df[subset_df['tumor_mask_empty'] == False]
    negatives = subset_df[subset_df['tumor_mask_empty'] == True]
    print(f"Positive samples (with tumor): {len(positives)}")
    print(f"Negative samples (no tumor): {len(negatives)}")

if __name__ == "__main__":
    main()
