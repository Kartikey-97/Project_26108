import json
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

random.seed(42)
np.random.seed(42)

def load_data():
    with open('data/ML_200_standards_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def group_split(data):
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
    return train_data, val_data, test_data

def main():
    data = load_data()
    train_data, val_data, test_data = group_split(data)
    
    X_train_raw = [d['requirement_text'] for d in train_data]
    y_train = [d['requirement_type'] for d in train_data]
    X_test_raw = [d['requirement_text'] for d in test_data]
    y_test = [d['requirement_type'] for d in test_data]
    
    all_labels = sorted(list(set([d['requirement_type'] for d in data])))
    
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)
    
    # 1. Random Forest
    rf_clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    rf_clf.fit(X_train, y_train)
    rf_preds = rf_clf.predict(X_test)
    
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_f1_macro = f1_score(y_test, rf_preds, average='macro', zero_division=0)
    rf_f1_weighted = f1_score(y_test, rf_preds, average='weighted', zero_division=0)
    
    # 2. LightGBM
    lgb_clf = lgb.LGBMClassifier(random_state=42, class_weight='balanced', n_estimators=100)
    lgb_clf.fit(X_train, y_train)
    lgb_preds = lgb_clf.predict(X_test)
    
    lgb_acc = accuracy_score(y_test, lgb_preds)
    lgb_f1_macro = f1_score(y_test, lgb_preds, average='macro', zero_division=0)
    lgb_f1_weighted = f1_score(y_test, lgb_preds, average='weighted', zero_division=0)
    
    # Print the table
    print("Model             Accuracy    Macro F1    Weighted F1")
    print(f"Random Forest      {rf_acc:.4f}       {rf_f1_macro:.4f}      {rf_f1_weighted:.4f}")
    print(f"LightGBM           {lgb_acc:.4f}       {lgb_f1_macro:.4f}      {lgb_f1_weighted:.4f}")
    
    print("\\n==================================================")
    print("RANDOM FOREST - PER CLASS METRICS")
    print("==================================================")
    print(classification_report(y_test, rf_preds, labels=all_labels, zero_division=0))
    print("Confusion Matrix:")
    print("Labels order:", all_labels)
    print(confusion_matrix(y_test, rf_preds, labels=all_labels))
    
    print("\\n==================================================")
    print("LIGHTGBM - PER CLASS METRICS")
    print("==================================================")
    print(classification_report(y_test, lgb_preds, labels=all_labels, zero_division=0))
    print("Confusion Matrix:")
    print("Labels order:", all_labels)
    print(confusion_matrix(y_test, lgb_preds, labels=all_labels))

if __name__ == "__main__":
    main()
