with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'r') as f:
    content = f.read()

old_pages = r"<span>{standard.pages} pages</span>"
new_pages = r"{standard.pages > 0 && <span>{standard.pages} pages</span>}"

content = content.replace(old_pages, new_pages)

with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'w') as f:
    f.write(content)
print("Fixed pages rendering")
