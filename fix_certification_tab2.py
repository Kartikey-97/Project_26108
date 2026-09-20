import re

with open('frontend/src/pages/analysis/AnalysisCertificationTab.tsx', 'r') as f:
    content = f.read()

# Replace the broken block
broken_block = """  // removed standard_intelligence block`,
        analysisId: analysis.id,
        requirement: `Compulsory Registration for ${std.standardTitle}`,
        type: 'qco',
        status: 'applicable',
        relatedStandard: std.standardCode,
        relatedStandardId: std.id,
        issuingAuthority: 'Bureau of Indian Standards / MeitY',
        sourceDocument: 'QCO Gazette Notification 2023',
        whyAppliesText: `Mandatory certification under the BIS Compulsory Registration Scheme as per QCO guidelines for ${std.standardCode}.`,
        whyAppliesCriteria: [{ text: 'Target entity classification', matched: true }],
        evidenceAvailable: true
     }));
  }"""

content = content.replace(broken_block, "")

with open('frontend/src/pages/analysis/AnalysisCertificationTab.tsx', 'w') as f:
    f.write(content)
