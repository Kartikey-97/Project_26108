with open('frontend/src/services/adapter.ts', 'r') as f:
    content = f.read()

import re

old_block_regex = r"  const regulatory: RegulatoryRequirement\[\] = standards\n    \.filter\(\(s\) => s\.regulatory\)\n    \.map\(\(s\) => \(\{\n      id: `reg-\$\{s\.id\}`,\n      analysisId,\n      requirement: `BIS certification — \$\{s\.number\}`,\n      type: 'certification',\n      status: 'applicable',\n      relatedStandard: s\.number,\n      relatedStandardId: s\.id,\n      issuingAuthority: 'Bureau of Indian Standards \(BIS\)',\n      sourceDocument: 'Quality Control Order notification',\n      whyAppliesText: s\.regulatoryNote \|\| `\$\{s\.number\} is notified under a Quality Control Order; BIS certification is mandatory for supply\.`,\n      whyAppliesCriteria: \[\],\n      evidenceAvailable: true,\n      reviewConfidence: 'high-confidence',\n    \}\)\);"

new_block = """  const regulatory: RegulatoryRequirement[] = standards
    .filter((s) => s.regulatory)
    .map((s) => {
      // Find the raw standard from get_analysis response if possible
      const rawS = raw?.standards?.find((rs: any) => String(rs.id) === String(s.id)) || {};
      return {
        id: `reg-${s.id}`,
        analysisId,
        requirement: `BIS certification — ${s.number}`,
        type: 'certification',
        status: 'applicable',
        relatedStandard: s.number,
        relatedStandardId: s.id,
        issuingAuthority: rawS.qco_issuing_ministry || 'Bureau of Indian Standards (BIS)',
        sourceDocument: 'Quality Control Order notification',
        orderNumber: rawS.qco_gazette_so_number || '-',
        effectiveDate: rawS.qco_effective_date || '-',
        whyAppliesText: s.regulatoryNote || `${s.number} is notified under a Quality Control Order; BIS certification is mandatory for supply.`,
        whyAppliesCriteria: [],
        evidenceAvailable: true,
        reviewConfidence: 'high-confidence',
      };
    });"""

match = re.search(old_block_regex, content)
if match:
    content = content.replace(match.group(0), new_block)
    with open('frontend/src/services/adapter.ts', 'w') as f:
        f.write(content)
    print("Fixed adapter QCO fields")
else:
    print("Could not find block in adapter.ts")
