with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'r') as f:
    content = f.read()

old_str = "a.number"
new_str = "(a.amendment_number || a.number)"

if old_str in content:
    content = content.replace(old_str, new_str)
    with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'w') as f:
        f.write(content)
    print("UI fixed successfully.")
else:
    print("Could not find a.number in UI file.")
