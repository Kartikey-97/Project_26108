import re

with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'r') as f:
    content = f.read()

content = content.replace(
"""import { useState, useEffect } from 'react';
import { API_ROOT, API_KEY } from '@/services/api';""",
"import { useState, useEffect } from 'react';")

content = content.replace("fetch(`${API_ROOT}/standards/bis-sync-status`, { headers: { 'X-API-Key': API_KEY } })",
                          "fetch('/api/v1/standards/bis-sync-status')")

with open('frontend/src/pages/analysis/AnalysisStandardsTab.tsx', 'w') as f:
    f.write(content)
