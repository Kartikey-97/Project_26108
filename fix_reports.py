import re

with open('frontend/src/pages/ReportsPage.tsx', 'r') as f:
    content = f.read()

# Pass props to ReportPreviewModal call
content = content.replace(
    "<ReportPreviewModal report={previewReport} onClose={() => setPreviewReport(null)} />",
    "<ReportPreviewModal report={previewReport} onClose={() => setPreviewReport(null)} isEmailing={isEmailing} handleEmailReport={handleEmailReport} />"
)

# Update ReportPreviewModal signature
old_sig = "function ReportPreviewModal({ report, onClose }: { report: Report; onClose: () => void }) {"
new_sig = "function ReportPreviewModal({ report, onClose, isEmailing, handleEmailReport }: { report: Report; onClose: () => void; isEmailing: string | null; handleEmailReport: (rId: string, aId: string) => void }) {"
content = content.replace(old_sig, new_sig)

# In ReportsPage.tsx, we saw another TS error:
# "Property 'tenderTitle' does not exist on type 'Analysis'."
content = content.replace("title: a.tenderTitle || a.id,", "title: a.title || a.id,")

with open('frontend/src/pages/ReportsPage.tsx', 'w') as f:
    f.write(content)
