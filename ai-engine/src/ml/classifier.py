import joblib
import os

class RequirementClassifier:
    def __init__(self, model_path="models/requirement_classifier.joblib"):
        self.model_path = model_path
        self.pipeline = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
            self.vectorizer = self.pipeline['vectorizer']
            self.classifier = self.pipeline['classifier']
            self.labels = self.pipeline['labels']
        else:
            print(f"Model not found at {self.model_path}. Please train the model first.")

    def predict(self, texts):
        if not self.pipeline:
            return ["OTHER"] * len(texts)
            
        X = self.vectorizer.transform(texts)
        preds = self.classifier.predict(X)
        return preds.tolist()

    def predict_single(self, text):
        return self.predict([text])[0]
