with open('frontend/src/pages/analysis/AnalysisGapsTab.tsx', 'r') as f:
    content = f.read()

content = content.replace("import { useState, useMemo } from 'react';", "import { useState, useMemo, useEffect } from 'react';")

with open('frontend/src/pages/analysis/AnalysisGapsTab.tsx', 'w') as f:
    f.write(content)
print("Added useEffect import")
