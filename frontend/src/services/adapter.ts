// Adapts the real FastAPI backend payloads (see services/api.js) into the
// improved-UI data model declared in data/types.ts. The backend returns
// { standards[], findings[], requirements[], tender_title, metadata, status, ... }
// while the UI tabs consume Analysis / Standard / SpecificationRequirement / etc.
import type {
  Analysis,
  AnalysisStatus,
  EvidenceChainItem,
  HumanReviewConfidence,
  MatchedRequirementItem,
  RegulatoryRequirement,
  SpecificationRequirement,
  Standard,
  StandardRelationship,
  StandardStatus,
} from '@/data/types';

/* eslint-disable @typescript-eslint/no-explicit-any */

// ---- small helpers ---------------------------------------------------------

function cleanTitle(raw = ''): string {
  const cutoffs = [' This standard is available', ' This Standard is available', 'NOTE -', 'Note -', '(Please refer', 'For Printed copies'];
  let t = raw;
  for (const c of cutoffs) {
    const idx = t.indexOf(c);
    if (idx > 20) t = t.slice(0, idx);
  }
  return t.trim().replace(/\s+/g, ' ');
}

// Backend confidence may arrive as 0..1 or 0..100 — normalise to 0..1.
function norm(c: unknown): number {
  const n = typeof c === 'number' ? c : Number(c) || 0;
  return n > 1 ? n / 100 : n;
}

function confBand(c: unknown): HumanReviewConfidence {
  const n = norm(c);
  if (n >= 0.75) return 'high-confidence';
  if (n >= 0.4) return 'needs-review';
  return 'insufficient-evidence';
}

function mapStandardStatus(status = ''): StandardStatus {
  const s = status.toLowerCase();
  if (s.includes('supersed')) return 'superseded';
  if (s.includes('withdraw')) return 'withdrawn';
  // backend enum: active | under_revision | reaffirmed | superseded | withdrawn | unknown
  if (s.includes('review') || s.includes('revis')) return 'under-review';
  if (s.includes('amend')) return 'amended';
  return 'current';
}

function mapAnalysisStatus(status = ''): AnalysisStatus {
  const s = status.toLowerCase();
  if (s === 'completed' || s === 'partially_completed') return 'completed';
  if (s === 'failed') return 'failed';
  // queued | extracting | retrieving | analyzing | enriching are all in-flight
  return 'processing';
}

// finding.verdict is one of ~11 backend verdicts; collapse to UI statuses.
function verdictToSpecStatus(verdict = ''): SpecificationRequirement['status'] {
  const v = verdict.toLowerCase();
  if (v === 'justified') return 'covered';
  if (v.includes('restrict')) return 'restrictive';
  if (v.includes('conflict')) return 'conflicting';
  if (v.includes('missing') || v.includes('not_found') || v.includes('absent')) return 'missing';
  return 'review';
}

function verdictToMatchedStatus(verdict = ''): MatchedRequirementItem['status'] {
  const v = verdict.toLowerCase();
  if (v === 'justified') return 'covered';
  if (v.includes('missing') || v.includes('not_found') || v.includes('absent')) return 'not-found';
  if (v.includes('partial')) return 'partial';
  return 'needs-review';
}

function verdictToEvidenceStatus(verdict = ''): EvidenceChainItem['status'] {
  const v = verdict.toLowerCase();
  if (v === 'justified') return 'supported';
  if (v.includes('missing') || v.includes('not_found') || v.includes('absent')) return 'not-found';
  if (v.includes('partial')) return 'partial';
  return 'needs-review';
}

// ---- standards -------------------------------------------------------------

export function adaptStandard(raw: any): Standard {
  const number = raw.designation || raw.is_number || raw.number || 'IS —';
  const title = cleanTitle(raw.title || raw.standardTitle || number);
  const references: string[] = raw.normative_references || raw.references || [];
  const scope = raw.scope || raw.text_excerpt || `Indian Standard specifying requirements for: ${title.slice(0, 120)}.`;
  const qco = Boolean(raw.qco_notified);
  const year = raw.year_published || raw.year || (raw.latest_version && Number(String(raw.latest_version).replace(/[^0-9]/g, ''))) || 0;

  return {
    id: String(raw.id ?? number),
    number,
    title,
    category: raw.division_council || raw.category || 'BIS Catalog',
    edition: String(raw.latest_version || raw.edition || year || ''),
    revision: raw.status ? String(raw.status).replace(/_/g, ' ') : 'Current',
    status: mapStandardStatus(raw.status),
    bureau: 'BIS',
    section: raw.ics_code || raw.section || '',
    yearPublished: Number(year) || 0,
    lastUpdatedDate: raw.transition_deadline || raw.last_updated_date,
    pages: raw.pages || 0,
    summary: scope,
    keywords: raw.keywords || [],
    referencedBy: raw.referenced_by || [],
    references,
    isCertified: qco,
    certificationBody: qco ? (raw.required_certification_scheme || 'BIS') : null,
    regulatory: qco,
    regulatoryNote: qco ? 'Notified under a Quality Control Order — BIS certification mandatory.' : null,
    supersededBy: raw.superseded_by || undefined,
    amendments: raw.amendments || [],
    internationalEquivalents: raw.ics_code ? [raw.ics_code] : [],
    technicalCoverage: raw.text_excerpt || undefined,
    whyApplies: raw.why_recommended || raw.text_excerpt || scope,
    applicabilityScore: typeof raw.relevance_score === 'number' ? Math.round(norm(raw.relevance_score) * 100) : undefined,
    evidenceAvailable: Array.isArray(raw.evidence) ? raw.evidence.length > 0 : undefined,
  };
}

// ---- full analysis ---------------------------------------------------------

export interface AdaptedAnalysis {
  analysis: Analysis;
  standards: Standard[];
  primaryStandard: Standard | null;
  matchedRequirements: MatchedRequirementItem[];
  specRequirements: SpecificationRequirement[];
  regulatory: RegulatoryRequirement[];
  evidence: EvidenceChainItem[];
  relationships: StandardRelationship[];
  degradedReason?: string | null;
  analysisMode?: string;
}

export function adaptAnalysis(raw: any): AdaptedAnalysis {
  const rawStandards: any[] = raw?.standards || [];
  const findings: any[] = raw?.findings || [];
  const requirements: any[] = raw?.requirements || [];

  const standards = rawStandards.map(adaptStandard);
  // The backend returns standards ranked by relevance; treat the top match as the
  // primary code so the Standards-tab "Primary" filter and highlight styling work.
  if (standards[0]) standards[0].relationshipRole = 'primary';
  const stdById = new Map(standards.map((s, i) => [String(rawStandards[i].id ?? s.id), s]));
  const findingFor = (reqId: string) => findings.find((f) => f.requirement_id === reqId);

  const analysisId = String(raw?.id ?? '');

  const matchedRequirements: MatchedRequirementItem[] = requirements.map((r) => {
    const f = findingFor(r.id);
    const std = f?.applicable_standards?.[0];
    return {
      id: r.id,
      requirement: r.text || r.category || 'Requirement',
      parameterValue: '', // backend requirements carry no separate value field

      standardCode: std?.designation || 'Not mapped',
      standardId: std?.id ? String(std.id) : '',
      clause: r.location || '',
      status: verdictToMatchedStatus(f?.verdict),
      evidenceSnippet: f?.evidence?.[0]?.excerpt,
      evidenceSource: f?.evidence?.[0]?.authority || f?.evidence?.[0]?.source_type,
      reviewConfidence: confBand(f?.confidence ?? r.extraction_confidence),
    };
  });

  const specRequirements: SpecificationRequirement[] = requirements.map((r) => {
    const f = findingFor(r.id);
    const std = f?.applicable_standards?.[0];
    return {
      id: r.id,
      analysisId,
      requirement: r.text || r.category || 'Requirement',
      tenderEvidence: f?.evidence?.[0]?.excerpt || r.text || '',
      tenderSection: r.location || r.category?.replace(/_/g, ' ') || '',
      applicableStandard: std?.designation || 'Not mapped',
      standardId: std?.id ? String(std.id) : '',
      clause: '',
      status: verdictToSpecStatus(f?.verdict),
      whyMatters: f?.reason || '',
      supportingEvidence: f?.evidence?.[0]?.excerpt,
      suggestedAction: f?.recommended_action,
      reviewConfidence: confBand(f?.confidence ?? r.extraction_confidence),
    };
  });

  const regulatory: RegulatoryRequirement[] = standards
    .filter((s) => s.regulatory)
    .map((s) => ({
      id: `reg-${s.id}`,
      analysisId,
      requirement: `BIS certification — ${s.number}`,
      type: 'certification',
      status: 'applicable',
      relatedStandard: s.number,
      relatedStandardId: s.id,
      issuingAuthority: 'Bureau of Indian Standards (BIS)',
      sourceDocument: 'Quality Control Order notification',
      whyAppliesText: s.regulatoryNote || `${s.number} is notified under a Quality Control Order; BIS certification is mandatory for supply.`,
      whyAppliesCriteria: [],
      evidenceAvailable: true,
      reviewConfidence: 'high-confidence',
    }));

  const evidence: EvidenceChainItem[] = findings.map((f) => {
    const r = requirements.find((x) => x.id === f.requirement_id);
    const ev = f.evidence?.[0];
    const std = f.applicable_standards?.[0];
    return {
      id: f.id,
      analysisId,
      requirement: r?.text || String(f.verdict || '').replace(/_/g, ' ') || 'Finding',
      standard: std?.designation || 'No mapped standard',
      standardId: std?.id ? String(std.id) : undefined,
      clause: '',
      evidence: ev?.excerpt || f.reason || '',
      sourceDoc: ev?.authority || ev?.source_type || 'Procurement analysis',
      sourceLocation: ev?.gazette_so_number || ev?.source_type || '',
      status: verdictToEvidenceStatus(f.verdict),
      conclusion: f.reason || '',
      reviewConfidence: confBand(f.confidence),
    };
  });

  const relationships: StandardRelationship[] = standards.flatMap((s) =>
    (s.references || []).slice(0, 4).map((ref, i) => ({
      id: `rel-${s.id}-${i}`,
      analysisId,
      fromStandardId: s.id,
      toStandardId: '',
      type: 'references' as const,
      label: `${s.number} → ${ref}`,
      description: `${s.number} cites ${ref} as a normative reference.`,
    })),
  );

  const gapsFound = findings.filter((f) => (f.verdict || '').toLowerCase() !== 'justified').length;
  const confidences = findings.map((f) => norm(f.confidence)).filter((n) => n > 0);
  const avgConfidence = confidences.length ? Math.round((confidences.reduce((a, b) => a + b, 0) / confidences.length) * 100) : 0;

  const analysis: Analysis = {
    id: analysisId,
    title: raw?.tender_title || raw?.metadata?.tender_title || 'Procurement analysis',
    category: raw?.metadata?.category || 'BIS analysis',
    status: mapAnalysisStatus(raw?.status),
    createdAt: raw?.created_at || '',
    completedAt: raw?.updated_at || null,
    documentCount: raw?.tender_id ? 1 : 0,
    standardsIdentified: standards.length,
    gapsFound,
    certificationsRequired: regulatory.length,
    confidence: avgConfidence,
    summary: raw?.degraded_reason || null,
    matchedStandardIds: standards.map((s) => s.id),
    gapIds: specRequirements.filter((s) => s.status !== 'covered').map((s) => s.id),
    documentIds: raw?.tender_id ? [String(raw.tender_id)] : [],
  };

  return {
    analysis,
    standards,
    primaryStandard: standards[0] || null,
    matchedRequirements,
    specRequirements,
    regulatory,
    evidence,
    relationships,
    degradedReason: raw?.degraded_reason ?? null,
    analysisMode: raw?.analysis_mode,
  };
}

// Summary rows for list pages (Reports / Workspace / History). The list endpoint
// returns { analysis_id, status, tender_title, total_requirements, issues_found, ... }
// and does NOT include standards/findings, so the gap count comes from issues_found.
export function adaptAnalysisSummary(raw: any): Analysis {
  return {
    id: String(raw?.analysis_id ?? raw?.id ?? ''),
    title: raw?.tender_title || raw?.title || 'Procurement analysis',
    category: raw?.metadata?.category || raw?.category || 'BIS analysis',
    status: mapAnalysisStatus(raw?.status),
    createdAt: raw?.created_at || '',
    completedAt: raw?.updated_at || null,
    documentCount: raw?.tender_id ? 1 : 0,
    standardsIdentified: 0,
    gapsFound: raw?.issues_found ?? 0,
    certificationsRequired: 0,
    confidence: 0,
    summary: raw?.summary || null,
    matchedStandardIds: [],
    gapIds: [],
    documentIds: [],
  };
}

export type StatusBadgeInfo = {
  label: string;
  variant: 'neutral' | 'teal' | 'blue' | 'success' | 'warning' | 'error' | 'outline';
};

// Map a raw backend analysis status (queued | extracting | retrieving | analyzing |
// enriching | completed | partially_completed | failed) → label + Badge variant.
export function statusBadge(status = ''): StatusBadgeInfo {
  switch (status.toLowerCase()) {
    case 'completed': return { label: 'Completed', variant: 'success' };
    case 'partially_completed': return { label: 'Partial', variant: 'warning' };
    case 'failed': return { label: 'Failed', variant: 'error' };
    case 'queued': return { label: 'Queued', variant: 'neutral' };
    case 'extracting': return { label: 'Extracting text', variant: 'blue' };
    case 'retrieving': return { label: 'Retrieving standards', variant: 'blue' };
    case 'analyzing': return { label: 'Analyzing', variant: 'blue' };
    case 'enriching': return { label: 'Enriching', variant: 'blue' };
    default: return { label: status ? status.replace(/_/g, ' ') : 'Unknown', variant: 'neutral' };
  }
}
