with open("/Users/kartikeygupta/Desktop/Hackathons/sih_26108/frontend/src/pages/analysis/AnalysisRelationshipsTab.tsx", "r") as f:
    lines = f.readlines()

# Find the start of the LED DEMO ONLY section
start_idx = -1
for i, line in enumerate(lines):
    if "─── LED DEMO ONLY ──" in line:
        start_idx = i
        break

# Find the end of the isReal section
end_idx = -1
for i, line in enumerate(lines[start_idx:]):
    if "1. RELATIONSHIP SUMMARY METRIC STRIP" in line:
        end_idx = start_idx + i - 1
        break

replacement = """  // ─── RELATIONSHIPS VIEW (FOR ALL ANALYSES) ─────────────────────────────────
  // Rich relationship card view dynamically driven by relationship data.
  const countByRole = (role: string) => rels.filter((r) => r.role === role).length;

  const roleSummary: Array<{ role: string; label: string; count: number }> = [
    { role: 'normative',    label: 'Normative Reference',         count: countByRole('normative') },
    { role: 'testing',      label: 'Testing Protocol',            count: countByRole('testing') },
    { role: 'safety',       label: 'Safety Standard',             count: countByRole('safety') },
    { role: 'installation', label: 'Design & Installation',       count: countByRole('installation') },
    { role: 'equivalent',   label: 'International Equivalent',    count: countByRole('equivalent') },
    { role: 'supersedes',   label: 'Superseded / Withdrawn',      count: countByRole('supersedes') },
  ].filter((s) => s.count > 0);

  if (rels.length === 0) {
    return (
      <div className="space-y-4">
        <Card padding="lg" className="bg-white border-ink-200 shadow-soft">
          <div className="flex items-center gap-2 border-b border-ink-100 pb-3 mb-4">
            <GitBranch size={16} className="text-teal-700" />
            <div>
              <h3 className="text-sm font-semibold text-ink-900">Standard References &amp; Relationships</h3>
              <p className="text-xs text-ink-500 mt-0.5">
                Normative references cited by the matched standards for this procurement.
              </p>
            </div>
          </div>
          <div className="py-10 text-center">
            <Share2 size={22} className="mx-auto mb-2 text-ink-300" />
            <p className="text-sm font-medium text-ink-700">No normative/cross-reference relationships identified.</p>
            <p className="mx-auto mt-1 max-w-sm text-xs text-ink-400">
              Relationships appear when a matched standard cites other Indian or international
              standards as normative references.
            </p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Summary count strip ─────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-2 pb-3 border-b border-ink-100">
        <span className="text-xs font-bold text-ink-700 mr-1 font-mono uppercase tracking-wider">
          Relationship Summary:
        </span>
        {roleSummary.length > 0 ? roleSummary.map(({ role, label, count }) => {
          const theme = getRoleTheme(role);
          return (
            <span
              key={role}
              className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold font-mono ${theme.badgeBg} ${theme.badgeText} border-current/30`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${theme.dot}`} />
              {count} {label}
            </span>
          );
        }) : (
           <span className="text-xs font-mono text-ink-500">{rels.length} Connected Standards</span>
        )}
      </div>

      {/* ── Relationship cards ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-5">
        {rels.map((rel) => {
          const theme = getRoleTheme(rel.role || 'normative');
          const fromStd = localGetStandardById(rel.fromStandardId);
          const toStd   = localGetStandardById(rel.toStandardId);
          const fromLabel = fromStd?.number ?? rel.fromStandardId;
          const toLabel   = toStd?.number   ?? rel.toStandardId;

          return (
            <div
              key={rel.id}
              className="rounded-xl border border-ink-200 bg-white shadow-soft hover:shadow-md transition-shadow overflow-hidden"
            >
              {/* Coloured top bar matching role */}
              <div className="h-1" style={{ backgroundColor: theme.stroke }} />

              <div className="p-5">
                {/* Card header: type badge + clause + title */}
                <div className="flex flex-wrap items-start gap-3 pb-4 mb-4 border-b border-ink-100">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span
                        className={`inline-block rounded px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest font-mono ${theme.badgeBg} ${theme.badgeText}`}
                      >
                        {theme.label}
                      </span>
                      {rel.clause && (
                        <span className="text-[11px] font-mono text-ink-400">{rel.clause}</span>
                      )}
                    </div>

                    {/* Source → Target */}
                    <div className="flex items-center gap-2 mt-1">
                      <button
                        onClick={() => fromStd && navigate({ name: 'standard', standardId: fromStd.id })}
                        className={`font-mono font-bold text-sm ${fromStd ? 'text-ink-900 hover:text-teal-700 underline underline-offset-2' : 'text-ink-600 cursor-default'}`}
                      >
                        {fromLabel}
                      </button>
                      <ArrowRight size={14} className="text-ink-400 shrink-0" />
                      <button
                        onClick={() => toStd && navigate({ name: 'standard', standardId: toStd.id })}
                        className={`font-mono font-bold text-sm ${toStd ? 'text-ink-900 hover:text-teal-700 underline underline-offset-2' : 'text-ink-600 cursor-default'}`}
                      >
                        {toLabel}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Content Sections */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Left Col: Explanation */}
                  <div className="space-y-4">
                    <div>
                      <h5 className="text-[11px] font-bold uppercase tracking-wider text-ink-500 font-mono mb-2 flex items-center gap-1.5">
                        <Link size={12} />
                        Nature of Relationship
                      </h5>
                      <p className="text-sm text-ink-700 leading-relaxed">{rel.description}</p>
                    </div>

                    {/* Procurement impact */}
                    {rel.whyMatters && (
                      <div>
                        <h5 className="text-[11px] font-bold uppercase tracking-wider text-teal-600 font-mono mb-2">
                          Procurement impact
                        </h5>
                        <p className="text-sm text-teal-900 leading-relaxed bg-teal-50/60 border border-teal-100 rounded-lg p-3">
                          {rel.whyMatters}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Right Col: Evidence Snippet (if any) */}
                  {rel.evidenceSnippet && (
                    <div className="md:border-l md:border-ink-100 md:pl-5 space-y-3">
                      <h5 className="text-[11px] font-bold uppercase tracking-wider text-amber-700 font-mono flex items-center gap-1.5">
                        <FileText size={12} />
                        Evidence in Standard
                      </h5>
                      <div className="rounded border border-amber-200/60 bg-amber-50/50 p-3 relative">
                        <Quote size={14} className="absolute text-amber-200 -top-1 -left-1" />
                        <p className="text-xs text-amber-900 italic leading-relaxed relative z-10 pl-2">
                          {rel.evidenceSnippet}
                        </p>
                      </div>
                      {rel.evidenceSource && (
                        <div className="text-[10px] font-mono text-ink-400 mt-2">
                          Source: {rel.evidenceSource}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
"""

new_lines = lines[:start_idx] + [replacement + "\n"] + lines[end_idx-1:]

with open("/Users/kartikeygupta/Desktop/Hackathons/sih_26108/frontend/src/pages/analysis/AnalysisRelationshipsTab.tsx", "w") as f:
    f.writelines(new_lines)
