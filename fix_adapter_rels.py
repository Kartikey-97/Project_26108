with open('frontend/src/services/adapter.ts', 'r') as f:
    content = f.read()

import re

old_block_regex = r"  const relationships: StandardRelationship\[\] = findings\.flatMap\(\(f\) =>\n    \(f\.cross_references \|\| \[\]\)\.flatMap\(\(xref: any, fi: number\) =>\n      \(xref\.references \|\| \[\]\)\.slice\(0, 4\)\.map\(\(ref: string, ri: number\) => \(\{\n        id: `rel-\$\{f\.id\}-\$\{fi\}-\$\{ri\}`,[\s\S]*?description: xref\.note \|\| `\$\{xref\.source_designation \|\| xref\.source\} cites \$\{ref\} as a normative reference\.`,\n      \}\)\),\n    \),\n  \);"

new_block = """  const relationships: StandardRelationship[] = findings.flatMap((f) =>
    (f.cross_references || []).flatMap((xref: any, fi: number) =>
      (xref.references || []).slice(0, 4).map((ref: string, ri: number) => ({
        id: `rel-${f.id}-${fi}-${ri}`,
        analysisId,
        fromStandardId: xref.source || '',
        toStandardId: '',
        type: 'references' as const,
        label: `${xref.source_designation || xref.source} → ${ref}`,
        description: xref.note || `${xref.source_designation || xref.source} cites ${ref} as a normative reference.`,
      })),
    ),
  );
  
  // Inject superseding relationships dynamically for real standards
  standards.forEach((std) => {
    if (std.supersededBy) {
      const cleanSup = std.supersededBy.replace(/\\s/g, '').toLowerCase();
      const newStd = standards.find(s => s.number.replace(/\\s/g, '').toLowerCase() === cleanSup || (s.title && s.title.replace(/\\s/g, '').toLowerCase() === cleanSup));
      if (newStd) {
        relationships.push({
          id: `rel-sup-${std.id}-${newStd.id}`,
          analysisId,
          fromStandardId: newStd.id,
          toStandardId: std.id,
          type: 'supersedes' as any,
          role: 'supersedes' as any,
          label: 'Superseded By',
          description: `Standard ${std.number} has been officially superseded by ${newStd.number}.`
        });
      }
    }
  });"""

match = re.search(old_block_regex, content)
if match:
    content = content.replace(match.group(0), new_block)
    with open('frontend/src/services/adapter.ts', 'w') as f:
        f.write(content)
    print("Fixed adapter relationships")
else:
    print("Could not find block in adapter.ts")
