import re

with open("frontend/src/pages/analysis/AnalysisStandardsTab.tsx", "r") as f:
    content = f.read()

# Remove all RefreshCw inserts
content = re.sub(r"import \{\n  RefreshCw, ", "import { ", content)
content = re.sub(r"import \{\n  RefreshCw,\n", "import {\n", content)

# ensure RefreshCw is imported in lucide-react
if "RefreshCw," not in content:
    content = content.replace("  AlertCircle,", "  AlertCircle,\n  RefreshCw,")

with open("frontend/src/pages/analysis/AnalysisStandardsTab.tsx", "w") as f:
    f.write(content)
