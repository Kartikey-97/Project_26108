with open('frontend/src/services/adapter.ts', 'r') as f:
    content = f.read()

import re

old_block_regex = r"        effectiveDate: rawS\.qco_effective_date \|\| '-',\n        whyAppliesText: s\.regulatoryNote \|\| `\$\{s\.number\} is notified under a Quality Control Order; BIS certification is mandatory for supply\.`,\n        whyAppliesCriteria: \[\],"

new_block = """        effectiveDate: rawS.qco_effective_date || '-',
        validityInfo: rawS.qco_effective_date ? `Effective from ${rawS.qco_effective_date}` : 'Active / Mandatory',
        whyAppliesText: s.regulatoryNote || `${s.number} is notified under a Quality Control Order; BIS certification is mandatory for supply.`,
        whyAppliesCriteria: [
          { text: `Standard ${s.number} is officially notified by ${rawS.qco_issuing_ministry || 'MeitY/DPIIT/BIS'}`, matched: true },
          { text: 'Mandatory BIS certification is required for vendor eligibility', matched: true }
        ],"""

match = re.search(old_block_regex, content)
if match:
    content = content.replace(match.group(0), new_block)
    with open('frontend/src/services/adapter.ts', 'w') as f:
        f.write(content)
    print("Fixed adapter QCO details")
else:
    print("Could not find block in adapter.ts")
