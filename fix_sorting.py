import re

with open('frontend/src/services/adapter.ts', 'r') as f:
    content = f.read()

old_block = """  const standards = rawStandards.map(adaptStandard);
  // The backend returns standards ranked by relevance; treat the top match as the
  // primary code so the Standards-tab "Primary" filter and highlight styling work.
  if (standards[0]) standards[0].relationshipRole = 'primary';
  const stdById = new Map(standards.map((s, i) => [String(rawStandards[i].id ?? s.id), s]));"""

new_block = """  const standards = rawStandards.map(adaptStandard);
  const stdById = new Map(standards.map((s, i) => [String(rawStandards[i].id ?? s.id), s]));
  
  // Sort standards by applicability score descending so the highest score is primary
  standards.sort((a, b) => (b.applicabilityScore || 0) - (a.applicabilityScore || 0));
  
  // The highest scored standard is the primary code
  if (standards[0]) standards[0].relationshipRole = 'primary';"""

content = content.replace(old_block, new_block)

with open('frontend/src/services/adapter.ts', 'w') as f:
    f.write(content)
