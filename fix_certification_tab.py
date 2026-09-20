import re

with open('frontend/src/pages/analysis/AnalysisCertificationTab.tsx', 'r') as f:
    content = f.read()

# Replace analysis.standards_intelligence with something valid or remove it
content = re.sub(r"if \(analysis\?.standards_intelligence\?.length > 0 && rawRequirements\.length === 0\) \{[^\}]+\}", 
                 "// removed standard_intelligence block", content)

with open('frontend/src/pages/analysis/AnalysisCertificationTab.tsx', 'w') as f:
    f.write(content)
