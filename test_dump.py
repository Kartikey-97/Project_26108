from backend.shared.models import Finding, Standard, StandardStatus

std = Standard(is_number="IS 10322", title="Test", status=StandardStatus.ACTIVE)
finding = Finding(requirement_id="req1", analysis_id="an1", verdict="justified", reason="r", confidence=0.9, applicable_standards=[std])
d = finding.model_dump(mode="json")
print("applicable_standards in dump:", "applicable_standards" in d)
print(d["applicable_standards"])
