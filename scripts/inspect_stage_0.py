"""
Inspection script for Prompt 4.7 Stage 0: Initial Integration Assessment.
"""
import hashlib
import json
from pathlib import Path
import duckdb
import joblib
import numpy as np

repo_root = Path(__file__).resolve().parent.parent

def inspect_model_artifact():
    model_path = repo_root / "models/research/prompt_4_6/heatsense_soh_estimator.joblib"
    meta_path = repo_root / "models/research/prompt_4_6/final_model_metadata.json"
    schema_path = repo_root / "models/research/prompt_4_6/final_feature_schema.json"
    
    # Hash calculation
    h = hashlib.sha256()
    with open(model_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    actual_hash = h.hexdigest()
    
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    pipeline = joblib.load(model_path)
    
    print("=== 1. MODEL ARTIFACT VERIFICATION ===")
    print(f"Path: {model_path}")
    print(f"Exists: {model_path.exists()}")
    print(f"Size: {model_path.stat().st_size} bytes")
    print(f"Computed SHA-256: {actual_hash}")
    print(f"Metadata SHA-256: {meta.get('file_hash_sha256')}")
    print(f"Hash Match: {actual_hash == meta.get('file_hash_sha256')}")
    print(f"Pipeline Steps: {[name for name, _ in pipeline.steps]}")
    for name, step in pipeline.steps:
        print(f"  Step '{name}': {step}")
        if hasattr(step, "coef_"):
            print(f"    Coefficients shape: {step.coef_.shape}")
            print(f"    Intercept: {step.intercept_}")
            print(f"    Alpha: {getattr(step, 'alpha', None)}")
        if hasattr(step, "statistics_"):
            print(f"    Imputer statistics length: {len(step.statistics_)}")
        if hasattr(step, "mean_"):
            print(f"    Scaler mean length: {len(step.mean_)}")
            print(f"    Scaler scale length: {len(step.scale_)}")
            
    print("\n=== 2. EXACT MODEL FEATURE SCHEMA & UNITS ===")
    print(f"Feature count: {len(schema['required_features'])}")
    
    # Load feature dictionary
    feat_dict_path = repo_root / "data/interim/mit_dataset/features/feature_dictionary.json"
    with open(feat_dict_path, "r", encoding="utf-8") as f:
        feat_dict = json.load(f)
        
    for idx, feat in enumerate(schema["required_features"]):
        info = feat_dict.get(feat, {})
        print(f"{idx+1:2d}. {feat:<24} | Units: {info.get('units', 'unknown'):<12} | Model: {info.get('model', 'unknown'):<8} | {info.get('description', '')}")

def inspect_host_architecture():
    print("\n=== 3. EXISTING HOST ARCHITECTURE INSPECTION ===")
    host_dir = repo_root / "host/src/heatsense"
    for py_file in sorted(host_dir.rglob("*.py")):
        rel = py_file.relative_to(host_dir)
        print(f"  - {rel}")

if __name__ == "__main__":
    inspect_model_artifact()
    inspect_host_architecture()
