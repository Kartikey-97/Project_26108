import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

def load_data():
    with open('data/ML_200_standards_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def group_split(data):
    # Group by standard ID
    std_to_records = {}
    for d in data:
        std_id = d['source_standard_id']
        if std_id not in std_to_records:
            std_to_records[std_id] = []
        std_to_records[std_id].append(d)
        
    std_ids = list(std_to_records.keys())
    random.shuffle(std_ids)
    
    n_train = int(len(std_ids) * 0.70)
    n_val = int(len(std_ids) * 0.15)
    
    train_stds = std_ids[:n_train]
    val_stds = std_ids[n_train:n_train+n_val]
    test_stds = std_ids[n_train+n_val:]
    
    train_data = [rec for sid in train_stds for rec in std_to_records[sid]]
    val_data = [rec for sid in val_stds for rec in std_to_records[sid]]
    test_data = [rec for sid in test_stds for rec in std_to_records[sid]]
    
    # Actually, we can combine train + val for fitting if we aren't using early stopping, 
    # but LightGBM can use the val set for early stopping
    return train_data, val_data, test_data

def evaluate(model_name, y_true, y_pred, labels):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)
    f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    return {
        "model": model_name,
        "acc": acc,
        "prec": prec,
        "rec": rec,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "cm": cm
    }

def main():
    print("Loading synthetic dataset...")
    data = load_data()
    train_data, val_data, test_data = group_split(data)
    print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
    
    # Extract features and targets
    X_train_raw = [d['requirement_text'] for d in train_data]
    y_train = [d['requirement_type'] for d in train_data]
    
    X_val_raw = [d['requirement_text'] for d in val_data]
    y_val = [d['requirement_type'] for d in val_data]
    
    X_test_raw = [d['requirement_text'] for d in test_data]
    y_test = [d['requirement_type'] for d in test_data]
    
    # Get all unique labels
    all_labels = sorted(list(set([d['requirement_type'] for d in data])))
    
    print("TF-IDF Vectorization...")
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
    X_train = vectorizer.fit_transform(X_train_raw)
    X_val = vectorizer.transform(X_val_raw)
    X_test = vectorizer.transform(X_test_raw)
    
    # 1. Random Forest
    print("\nTraining Random Forest...")
    rf_clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    rf_clf.fit(X_train, y_train)
    rf_preds = rf_clf.predict(X_test)
    rf_metrics = evaluate("Random Forest", y_test, rf_preds, all_labels)
    
    # 2. LightGBM
    print("Training LightGBM...")
    lgb_clf = lgb.LGBMClassifier(random_state=42, class_weight='balanced', n_estimators=100)
    lgb_clf.fit(X_train, y_train)
    lgb_preds = lgb_clf.predict(X_test)
    lgb_metrics = evaluate("LightGBM", y_test, lgb_preds, all_labels)
    
    # 3. Report
    print("\n==================================================")
    print("MODEL COMPARISON REPORT")
    print("==================================================")
    print(f"{'Model':<15} | {'Accuracy':<10} | {'Macro F1':<10} | {'Weighted F1':<10}")
    print("-" * 55)
    print(f"{rf_metrics['model']:<15} | {rf_metrics['acc']:.4f}     | {rf_metrics['f1_macro']:.4f}   | {rf_metrics['f1_weighted']:.4f}")
    print(f"{lgb_metrics['model']:<15} | {lgb_metrics['acc']:.4f}     | {lgb_metrics['f1_macro']:.4f}   | {lgb_metrics['f1_weighted']:.4f}")
    
    # Select Best Model
    best_model_name = "Random Forest" if rf_metrics['f1_macro'] >= lgb_metrics['f1_macro'] else "LightGBM"
    print(f"\n[SELECTED MODEL]: {best_model_name} (Based on Macro F1)")
    
    best_clf = rf_clf if best_model_name == "Random Forest" else lgb_clf
    best_metrics = rf_metrics if best_model_name == "Random Forest" else lgb_metrics
    
    print("\n[CONFUSION MATRIX]")
    print("Labels order:", all_labels)
    print(best_metrics['cm'])
    
    # 4. Save best model pipeline
    print("\nSaving best model and vectorizer...")
    pipeline = {
        'vectorizer': vectorizer,
        'classifier': best_clf,
        'labels': all_labels,
        'selected_model_name': best_model_name
    }
    joblib.dump(pipeline, 'models/requirement_classifier.joblib')
    print("Saved to models/requirement_classifier.joblib")

if __name__ == "__main__":
    main()
