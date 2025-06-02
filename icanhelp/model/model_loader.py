# model_loader.py
import os
from sentence_transformers import SentenceTransformer

_model = None

def get_model(model_path="models/finetune_all-MiniLM-L6-v2"):
    global _model
    if _model is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_dir, model_path)
        _model = SentenceTransformer(full_path)
    return _model
