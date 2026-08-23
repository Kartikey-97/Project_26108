import sys
import os
import json
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def evaluate_model():
    print("Loading test data...")
    with open('data/ML_200_standards_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Recreate the exact split (or load if saved). Here we just evaluate the entire thing for demonstration,
    # since train.py does the strict train/test split. But let's load the model.
    print("Loading model pipeline...")
    if not os.path.exists('models/requirement_classifier.joblib'):
        print("Model not found. Run train.py first.")
        return
        
    pipeline = joblib.load('models/requirement_classifier.joblib')
    vectorizer = pipeline['vectorizer']
    classifier = pipeline['classifier']
    labels = pipeline['labels']
    model_name = pipeline['selected_model_name']
    
    texts = [d['requirement_text'] for d in data]
    y_true = [d['requirement_type'] for d in data]
    
    X = vectorizer.transform(texts)
    y_pred = classifier.predict(X)
    
    acc = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    
    print("\n==================================================")
    print("EVALUATION REPORT")
    print("==================================================")
    print(f"Model: {model_name}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro F1: {f1_macro:.4f}")
    print(f"Weighted F1: {f1_weighted:.4f}")

if __name__ == "__main__":
    evaluate_model()
