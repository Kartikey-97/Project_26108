// Mock Data for AI-Powered Procurement Recommendation Engine (BIS)

export const MOCK_STATS = [
  {
    id: 'stat-1',
    title: 'Total Analyses Run',
    value: '1',
    change: '+1 this week',
    trend: 'up',
    description: 'Procurement specs processed'
  },
  {
    id: 'stat-2',
    title: 'Applicable Standards Mapped',
    value: '0',
    change: 'Covering 0 categories',
    trend: 'neutral',
    description: 'Active Indian Standards (BIS)'
  },
  {
    id: 'stat-3',
    title: 'Avg. Completeness Score',
    value: '0%',
    change: 'No data',
    trend: 'neutral',
    description: 'Tender specification quality'
  },
  {
    id: 'stat-4',
    title: 'Restrictive Clauses Flagged',
    value: '0',
    change: 'No warnings',
    trend: 'neutral',
    description: 'Single-vendor bias warnings'
  }
];

export const MOCK_RECENT_ANALYSES = [
  {
    id: 'ANA-2026-089',
    title: 'Procurement of 120W Smart LED Street Lighting Luminaires',
    category: 'Electrical & Lighting',
    department: 'Public Works Dept (NH-44 Project)',
    date: '2026-08-22',
    standardsCount: 4,
    standards: ['IS 10322 (Part 5/Sec 3)', 'IS 16102 (Part 1)', 'IS 15885 (Part 2/Sec 13)'],
    completenessScore: 92,
    status: 'COMPLETED',
    qcoMandatory: true,
    flaggedIssues: 1
  },
  {
    id: 'ANA-2026-088',
    title: 'Supply of Submersible Solar Photovoltaic Water Pumping Systems',
    category: 'Renewable Energy',
    department: 'Ministry of Jal Shakti',
    date: '2026-08-20',
    standardsCount: 3,
    standards: ['IS 17018', 'IS 14286', 'IS 16107'],
    completenessScore: 85,
    status: 'WARNING_FLAGGED',
    qcoMandatory: true,
    flaggedIssues: 2
  },
  {
    id: 'ANA-2026-087',
    title: 'High Voltage Outdoor Oil-Immersed Power Transformers (11kV/415V)',
    category: 'Power Infrastructure',
    department: 'State Electricity Transmission Corp',
    date: '2026-08-18',
    standardsCount: 5,
    standards: ['IS 2026 (Part 1-5)', 'IS 1180 (Part 1)', 'IS 335'],
    completenessScore: 96,
    status: 'COMPLETED',
    qcoMandatory: true,
    flaggedIssues: 0
  },
  {
    id: 'ANA-2026-086',
    title: 'Structural Grade High-Strength Thermo-Mechanically Treated (TMT) Steel Bars',
    category: 'Civil & Construction',
    department: 'National Highways Authority of India',
    date: '2026-08-15',
    standardsCount: 2,
    standards: ['IS 1786: 2008', 'IS 2062'],
    completenessScore: 78,
    status: 'IN_REVIEW',
    qcoMandatory: true,
    flaggedIssues: 1
  }
];

export const MOCK_QUICK_ACTIONS = [
  {
    id: 'act-1',
    title: 'New Procurement Analysis',
    description: 'Paste text specifications or upload PDF/DOCX to identify relevant BIS standards.',
    actionText: 'Start Analysis',
    link: '/analyze',
    badge: 'AI Core',
    color: 'indigo'
  },
  {
    id: 'act-2',
    title: 'Indian Standards Explorer',
    description: 'Search authoritative Indian Standards database across engineering domains.',
    actionText: 'Explore Database',
    link: '/standards',
    badge: 'BIS Repository',
    color: 'emerald'
  },
  {
    id: 'act-3',
    title: 'Compare Specifications',
    description: 'Compare multiple standards side-by-side to eliminate technical ambiguities.',
    actionText: 'Compare Standards',
    link: '/compare',
    badge: 'Comparison Tool',
    color: 'amber'
  }
];

export const PRODUCT_CATEGORIES = [
  'Electrical & Lighting',
  'Civil & Construction Materials',
  'Renewable Energy & Solar',
  'Power Infrastructure & Transformers',
  'Mechanical Equipment & Pumps',
  'Water Supply & Pipe Infrastructure',
  'Electronics & Telecommunication'
];

export const INDUSTRY_DOMAINS = [
  'Roads & Highway Infrastructure',
  'Urban Development & Municipal Utilities',
  'Water Resources & Irrigation',
  'Power Generation & Distribution',
  'Public Building Construction',
  'Railway & Transport Systems'
];

export const PRESET_SPEC_SAMPLES = [
  {
    id: 'sample-led',
    label: 'LED Street Lighting (120W)',
    category: 'Electrical & Lighting',
    domain: 'Roads & Highway Infrastructure',
    department: 'Public Works Department (PWD)',
    text: `Procurement of 120W Smart Outdoor LED Street Lighting Luminaires for Highway Expansion.
Technical Requirements:
1. System Wattage: 120W ± 5%, Operating Voltage: 140V - 270V AC, 50Hz.
2. Luminous Efficacy: Minimum 130 lm/W (BEE 5-Star Rating).
3. Ingress Protection: IP 66 rating for optical & driver compartments.
4. Surge Protection: External 10 kV Surge Protection Device (SPD).
5. Correlated Color Temperature (CCT): Strictly 5700K ± 50K.
6. Total Harmonic Distortion (THD): ≤ 10%, Power Factor ≥ 0.95.
7. Compliance: Mandatory BIS CRS Registration & QCO Mark. Housing die-cast ADC12 powder coated.`
  }
];

export const MOCK_EXTRACTED_SUMMARY = {
  product: 'Smart Outdoor LED Street Lighting Luminaire',
  category: 'Electrical & Lighting',
  material: 'Die-Cast Aluminum Alloy ADC12 (Powder Coated)',
  application: 'Highway & Expressway Public Lighting (NH-44)',
  environment: 'Outdoor Heavy Duty High-Humidity Road Grid'
};

export const MOCK_EXTRACTED_REQUIREMENTS = [
  {
    id: 'req-1',
    type: 'TECHNICAL',
    parameter: 'System Wattage & Voltage',
    specifiedValue: '120W ± 5% (Operating 140V - 270V AC, 50Hz)',
    confidence: 0.98,
    status: 'VALID',
    governingStandard: 'IS 10322 (Part 5/Sec 3)'
  },
  {
    id: 'req-2',
    type: 'TECHNICAL',
    parameter: 'Luminous Efficacy',
    specifiedValue: '≥ 130 lm/W (BEE 5-Star Schedule compliant)',
    confidence: 0.96,
    status: 'VALID',
    governingStandard: 'IS 10322 / BEE Guidelines'
  },
  {
    id: 'req-3',
    type: 'TECHNICAL',
    parameter: 'Correlated Color Temp (CCT)',
    specifiedValue: 'Strictly 5700K ± 50K Only',
    confidence: 0.91,
    status: 'RESTRICTIVE_FLAG',
    governingStandard: 'IS 16102 (Part 2)',
    note: 'Narrow tolerance (± 50K) flagged for single-vendor lock-in risk.'
  },
  {
    id: 'req-4',
    type: 'SAFETY',
    parameter: 'Surge Protection Device (SPD)',
    specifiedValue: 'External 10 kV / 10 kA SPD',
    confidence: 0.95,
    status: 'VALID',
    governingStandard: 'IS 16102 (Part 1) / Amd 2'
  },
  {
    id: 'req-5',
    type: 'SAFETY',
    parameter: 'Regulatory BIS CRS Compliance',
    specifiedValue: 'Mandatory BIS Registration Mark on Housing & Driver',
    confidence: 0.99,
    status: 'VALID',
    governingStandard: 'QCO S.O. 2021(E) / IS 10322'
  },
  {
    id: 'req-6',
    type: 'PERFORMANCE',
    parameter: 'Ingress Protection (IP Rating)',
    specifiedValue: 'IP 66 Minimum (Optical & Control Gear)',
    confidence: 0.97,
    status: 'VALID',
    governingStandard: 'IS 10322 (Part 5/Sec 3)'
  },
  {
    id: 'req-7',
    type: 'PERFORMANCE',
    parameter: 'Total Harmonic Distortion (THD)',
    specifiedValue: 'THD ≤ 10%, Power Factor ≥ 0.95',
    confidence: 0.94,
    status: 'VALID',
    governingStandard: 'IS 15885 (Part 2/Sec 13)'
  }
];

export const MOCK_RECOMMENDED_STANDARDS = [
  {
    id: 'IS-10322-5-3',
    rank: 1,
    standardCode: 'IS 10322 (Part 5/Sec 3): 2012',
    standardTitle: 'Luminaires - Particular Requirements - Luminaires for Street and Highway Lighting',
    category: 'Electrical & Street Lighting',
    matchPercentage: 98,
    applicability: 'MANDATORY (QCO)',
    isQcoMandatory: true,
    statusBadge: 'CURRENT',
    matchedRequirements: ['System Wattage (120W)', 'Ingress Protection (IP66)', 'Mechanical Housing ADC12', 'Photometric Distribution'],
    aiExplanation: 'Primary governing standard for outdoor roadway luminaires. Clause 6.3 mandates IP65/IP66 ingress protection and Clause 7.1 establishes luminous efficacy limits for public tenders.',
    normativeRefs: ['IS 10322 (Part 1)', 'IS 16102 (Part 1)', 'IS 15885 (Part 2/Sec 13)']
  },
  {
    id: 'IS-16102-1',
    rank: 2,
    standardCode: 'IS 16102 (Part 1): 2012',
    standardTitle: 'Self-Ballasted LED Lamps for General Lighting Services - Safety Requirements',
    category: 'LED Safety & Modules',
    matchPercentage: 94,
    applicability: 'MANDATORY (QCO)',
    isQcoMandatory: true,
    statusBadge: 'AMENDED (Amd 2)',
    matchedRequirements: ['Surge Protection 10kV', 'Dielectric Strength', 'Torque Safety', 'Insulation Resistance'],
    aiExplanation: 'Mandates safety testing and surge protection for LED modules. Amendment 2 (2021) requires external 10kV SPD protection for outdoor highway installations.',
    normativeRefs: ['IS 6863: 1973', 'IS 10322 (Part 1)']
  },
  {
    id: 'IS-15885-2-13',
    rank: 3,
    standardCode: 'IS 15885 (Part 2/Sec 13): 2012',
    standardTitle: 'Lamp Control Gear - Particular Requirements for DC or AC Supplied Electronic Control Gear for LED Modules',
    category: 'Driver & Electronic Control Gear',
    matchPercentage: 91,
    applicability: 'NORMATIVE REFERENCE',
    isQcoMandatory: true,
    statusBadge: 'CURRENT',
    matchedRequirements: ['Total Harmonic Distortion (THD ≤ 10%)', 'Power Factor (≥ 0.95)', 'Thermal Overload Protection'],
    aiExplanation: 'Governs electronic LED driver performance. Clause 14.1 restricts input current harmonic distortion (THD) to ≤ 10% under full rated load.',
    normativeRefs: ['IS 15885 (Part 1)', 'IS 14700 (Part 3/Sec 2)']
  },
  {
    id: 'IS-16102-2',
    rank: 4,
    standardCode: 'IS 16102 (Part 2): 2012',
    standardTitle: 'Self-Ballasted LED Lamps for General Lighting Services - Performance Requirements',
    category: 'LED Photometrics & Chromaticity',
    matchPercentage: 84,
    applicability: 'RECOMMENDED',
    isQcoMandatory: false,
    statusBadge: 'CURRENT',
    matchedRequirements: ['Correlated Color Temperature (CCT)', 'Lumen Maintenance (L70)', 'Color Rendering Index (CRI)'],
    aiExplanation: 'Defines standard chromaticity tolerance ranges (± 300K). Used by AI engine to detect overly restrictive single-vendor CCT clauses (e.g. ± 50K).',
    normativeRefs: ['IS 16102 (Part 1)']
  }
];

export const MOCK_WHY_RECOMMENDED = [
  {
    id: 'why-1',
    tenderTextSnippet: 'Ingress Protection: IP 66 Minimum (Optical & Control Compartment)',
    requirement: 'IP 66 Ingress Protection',
    standardCode: 'IS 10322 (Part 5/Sec 3): 2012',
    mappedClause: 'Clause 6.3 - Dust & Water Resistance',
    standardClauseText: 'Luminaires for highway and roadway outdoor lighting shall achieve an ingress protection rating of not less than IP65 for optical assembly and IP65 for control gear compartment. IP66 is fully supported.',
    aiJustification: 'The tender requirement of IP66 directly satisfies and exceeds the baseline IP65 mandate of Clause 6.3 for outdoor street lighting luminaires.',
    confidence: 0.98,
    matchType: 'FULL_COVERAGE'
  },
  {
    id: 'why-2',
    tenderTextSnippet: 'Surge Protection: External 10 kV / 10 kA Surge Protection Device (SPD)',
    requirement: '10 kV Surge Protection',
    standardCode: 'IS 16102 (Part 1) / Amd 2: 2021',
    mappedClause: 'Clause 12.4 - Transient Immunity',
    standardClauseText: 'For luminaires deployed in severe surge outdoor environments (such as highway grids), an external Surge Protection Device (SPD) rated for at least 10 kV/10 kA tested as per IS/IEC 61643-11 shall be incorporated.',
    aiJustification: 'IS 16102 Amendment 2 explicitly mandates external 10kV SPD protection for outdoor road installations to prevent surge failure during monsoon lighting events.',
    confidence: 0.96,
    matchType: 'FULL_COVERAGE'
  }
];

export const MOCK_EVIDENCE_MAP = MOCK_WHY_RECOMMENDED;

export const MOCK_MISSING_REQUIREMENTS = [
  {
    id: 'miss-1',
    parameter: 'Aluminum Housing Alloy Standard (IS 617 Citation)',
    category: 'Material & Structural Integrity',
    severity: 'RECOMMENDED_ADDITION',
    missingExplanation: 'The tender specifies die-cast ADC12 aluminum housing but omits citing IS 617 (Aluminum Casting Alloy standard). Omitting IS 617 weakens legal defensibility during quality disputes.',
    suggestedClauseText: 'Housing material shall be high-pressure die-cast aluminum alloy ADC12 conforming to Grade 4600 of IS 617: 1994 (Reaffirmed 2020) with minimum 100-hour salt spray corrosion resistant powder coating.'
  },
  {
    id: 'miss-2',
    parameter: 'Electromagnetic Compatibility & Harmonics (IS 14700)',
    category: 'Electromagnetic Safety (EMC)',
    severity: 'RECOMMENDED_ADDITION',
    missingExplanation: 'Missing EMC immunity clause under IS 14700 (Part 3/Sec 2) to ensure driver does not interfere with wireless telecommunication towers along highways.',
    suggestedClauseText: 'Electronic control gear shall comply with harmonic current emission limits as per IS 14700 (Part 3/Sec 2): 2008 and immunity requirements as per IS 14700 (Part 4/Sec 5).'
  }
];

export const MOCK_COMPLETENESS_DATA = {
  overallScore: 92,
  grade: 'A+',
  statusText: 'Highly Complete Specification',
  summaryText: 'Specification covers 92% of governing Indian Standard clauses. CCT tolerance clause flagged for potential single-vendor bias.',
  categoryScores: [
    { name: 'Electrical & Safety Clauses', score: 96 },
    { name: 'Ingress & Environmental Protection', score: 94 },
    { name: 'Photometric & Performance Standards', score: 90 },
    { name: 'Material Grades & Corrosion Tests', score: 88 }
  ],
  strengths: [
    'Mandatory BIS CRS Registration & DPIIT Quality Control Order (QCO) explicitly enforced.',
    'External 10kV Surge Protection Device (SPD) specified in compliance with IS 16102 Amendment 2.',
    'IP66 ingress protection rating specified for optical and control compartments.'
  ],
  areasForImprovement: [
    'Append IS 617 aluminum casting alloy standard reference to prevent non-standard metal usage.',
    'Broaden CCT tolerance from ±50K to standard ±355K (IS 16102 Part 2) to eliminate vendor lock-in.'
  ]
};

export const MOCK_STANDARD_DETAIL_SINGLE = {
  standardCode: 'IS 10322 (Part 5/Sec 3): 2012',
  standardTitle: 'Luminaires - Particular Requirements - Luminaires for Street and Highway Lighting',
  category: 'Electrical & Street Lighting',
  currentVersion: 'IS 10322 (Part 5/Sec 3): 2012 (Reaffirmed 2022)',
  statusBadge: 'CURRENT & REAFFIRMED',
  applicability: 'MANDATORY (DPIIT QCO Order)',
  isQcoMandatory: true,
  internationalEquivalent: 'IEC 60598-2-3: 2011 (Identical Adoption)',
  overview: 'This standard specifies particular safety and performance requirements for luminaires used in public road, highway, expressway, and street lighting installations operating on electrical power supplies up to 1000V.',
  whyRecommended: 'Identified as the primary governing Indian Standard for your procurement specification. It directly satisfies the 120W rating, IP66 enclosure requirement, and die-cast housing parameters specified in the tender.',
  relevantSections: [
    { section: 'Section 4', title: 'Mechanical Construction & Corrosion Resistance', details: 'Housing shall withstand 100-hour salt spray corrosion test and vibration testing.' },
    { section: 'Section 6', title: 'Ingress Protection & Thermal Tests', details: 'Optical assembly shall maintain IP65 minimum. Operating temp range -10°C to +50°C.' },
    { section: 'Section 7', title: 'Photometric & Efficacy Requirements', details: 'System luminous efficacy minimum 100 lm/W (5-Star BEE rating mandates ≥ 120 lm/W).' },
    { section: 'Section 12', title: 'Transient Surge Protection & Control Gear Integration', details: 'Driver compartment shall house external SPD rated for minimum 10 kV/10 kA.' }
  ]
};

export const MOCK_COMPARISON_MATRIX = {
  standards: [
    {
      id: 'IS-10322-5-3',
      standardCode: 'IS 10322 (Part 5/Sec 3)',
      standardTitle: 'Street Lighting Luminaires (Roadways & Highways)',
      isBestMatch: true,
      rank: 1,
      matchPercentage: 98,
      isQcoMandatory: true,
      statusBadge: 'CURRENT',
      operatingVoltage: '140V - 270V AC',
      ipRating: 'IP 65 / IP 66 Mandated',
      surgeProtection: '10 kV / 10 kA SPD Required',
      thermalDissipation: 'Die-cast ADC12 (-10°C to +50°C)',
      testMethods: 'IS 10322 (Part 1) Clause 6.3'
    },
    {
      id: 'IS-16102-1',
      standardCode: 'IS 16102 (Part 1)',
      standardTitle: 'Self-Ballasted LED Lamps (Safety Requirements)',
      isBestMatch: false,
      rank: 2,
      matchPercentage: 94,
      isQcoMandatory: true,
      statusBadge: 'AMENDED',
      operatingVoltage: '150V - 265V AC',
      ipRating: 'General Safety Enclosure',
      surgeProtection: '10 kV External SPD (Amd 2)',
      thermalDissipation: 'Dielectric Insulation Test',
      testMethods: 'IS 6863 / IS 16102 Part 1'
    }
  ]
};

export const MOCK_FULL_HISTORY_LIST = MOCK_RECENT_ANALYSES;

export const MOCK_EXPLORER_STANDARDS = [
  {
    id: 'exp-1',
    standardCode: 'IS 10322 (Part 5/Sec 3): 2012',
    title: 'Luminaires - Particular Requirements - Luminaires for Street & Highway Lighting',
    category: 'Electrical & Lighting',
    statusBadge: 'CURRENT',
    reaffirmedYear: '2022',
    scope: 'Mandates safety, IP65/IP66 ingress protection, and thermal rules for outdoor public road lighting.'
  },
  {
    id: 'exp-2',
    standardCode: 'IS 16102 (Part 1): 2012',
    title: 'Self-Ballasted LED Lamps for General Lighting Services - Safety Requirements',
    category: 'Electrical & Lighting',
    statusBadge: 'AMENDED',
    reaffirmedYear: '2022',
    scope: 'Safety parameters, dielectric strength, and external 10kV Surge Protection Device (SPD) mandates.'
  },
  {
    id: 'exp-3',
    standardCode: 'IS 15885 (Part 2/Sec 13): 2012',
    title: 'Electronic Control Gear for LED Modules - Performance & Safety',
    category: 'Electrical & Lighting',
    statusBadge: 'CURRENT',
    reaffirmedYear: '2020',
    scope: 'Regulates LED electronic driver current distortion (THD ≤ 10%) and thermal overload cutoff.'
  },
  {
    id: 'exp-4',
    standardCode: 'IS 1786: 2008',
    title: 'High Strength Deformed Steel Bars and Wires for Concrete Reinforcement (TMT Rebars)',
    category: 'Civil & Construction Materials',
    statusBadge: 'CURRENT',
    reaffirmedYear: '2021',
    scope: 'Defines chemical limits (Carbon, Sulfur, Phosphorus) and mechanical elongation for Fe 500D TMT rebars.'
  }
];

export const MOCK_BIS_CATALOG_FULL = MOCK_EXPLORER_STANDARDS;
