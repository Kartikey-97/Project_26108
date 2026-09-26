import re

with open('frontend/src/pages/NewAnalysisPage.tsx', 'r') as f:
    content = f.read()

# Fix useEffect import
content = re.sub(r"import \{ useRef, useState \} from 'react';", 
                 "import { useRef, useState, useEffect } from 'react';", content)

# Fix getBackendHealth import
content = re.sub(r"import \{ createAnalysis, waitForAnalysis, getSampleDocument, extractProfilePreview \} from '@/services/api';",
                 "import { createAnalysis, waitForAnalysis, getSampleDocument, extractProfilePreview, getBackendHealth } from '@/services/api';", content)

with open('frontend/src/pages/NewAnalysisPage.tsx', 'w') as f:
    f.write(content)
