with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'r') as f:
    content = f.read()

old_link = '<a href={standard.bisSourceUrl} target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:underline">BIS source ↗</a>'
new_link = '<a href={standard.bisSourceUrl === "https://standards.bis.gov.in" ? "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/knowyourstandards/indian_standards/isdetails" : standard.bisSourceUrl} title="Copy the IS number and paste it in the BIS search portal" target="_blank" rel="noopener noreferrer" className="text-teal-600 hover:underline">BIS Search Portal ↗</a>'

content = content.replace(old_link, new_link)
with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'w') as f:
    f.write(content)
print("Fixed BIS link")
