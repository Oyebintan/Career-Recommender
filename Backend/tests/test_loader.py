# tests/test_loader.py
"""
Run from the Backend/ directory:
    python tests/test_loader.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.dataset_loader import DatasetLoader

loader = DatasetLoader()
datasets = loader.load_all()

print("\nCAREER PROFILES")
print(datasets["profiles"].head())
print("\nCAREER SKILLS")
print(datasets["skills"].head())
print("\nQUESTIONS")
print(datasets["questions"].head())
print("\nMAPPINGS")
print(datasets["mappings"].head())
print("\nDESCRIPTIONS")
print(datasets["descriptions"].head())
print("\nSUCCESS: ALL DATASETS LOADED")