import os
import uuid
from src.ml.classifier import RequirementClassifier
from src.reasoning.providers.mock import MockReasoner

class Analyzer:
    def __init__(self):
        self.classifier = RequirementClassifier()
        mode = os.getenv("AI_MODE", "mock")
        if mode == "mock":
            self.provider = MockReasoner()
        else:
            self.provider = MockReasoner() # Fallback for now

    def process(self, request):
        findings = []
        for req in request.requirements:
            # 1. ML Classification
            req_type = self.classifier.predict_single(req.text)
            
            # 2. Deterministic rules
            outdated_stds = [s for s in request.retrieved_standards if s.status.lower() in ['superseded', 'withdrawn']]
            
            # 3. LLM Reasoning (via provider)
            res = self.provider.analyze(req.text, req_type, request.retrieved_standards)
            
            if outdated_stds:
                verdict = "outdated_reference"
                reason = "The referenced standard is marked superseded or withdrawn in the supplied BIS metadata."
                action = "Update the tender specification."
                conf = 1.0
            else:
                verdict = res["verdict"]
                reason = res["reason"]
                action = res["action"]
                conf = res["confidence"]
                
            finding = {
                "finding_id": str(uuid.uuid4()),
                "requirement_id": req.id,
                "verdict": verdict,
                "reason": reason,
                "recommended_action": action,
                "applicable_standard_ids": [s.id for s in request.retrieved_standards],
                "evidence_ids": [],
                "confidence": conf
            }
            findings.append(finding)
            
        return {
            "analysis_id": request.analysis_id,
            "findings": findings,
            "extraction_metadata": {
                "ml_model_used": "RandomForest_TFIDF",
                "reasoning_mode": os.getenv("AI_MODE", "mock")
            }
        }
