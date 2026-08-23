// Mock Procurement Analysis Data following the agreed API Contract
// Category: LED Street & Highway Lighting Procurement (SIH 2026 PS 26108 Proof-of-Concept)

export const MOCK_LED_LIGHTING_DATA = {
  procurement_id: "PROC-2026-LED-8891",
  created_at: "2026-08-22T20:20:00Z",
  status: "ANALYSIS_COMPLETE",
  input_summary: {
    title: "Procurement of 120W Smart LED Street Lighting Luminaires for NH-44 Highway Expansion",
    category: "Lighting & Luminaires",
    source_type: "Technical Tender Document / Custom Requirement",
    department: "National Highways Authority of India (NHAI) / Public Works Dept",
    total_specs_extracted: 7,
    overall_risk_score: "MEDIUM",
    qco_mandatory: true,
    bis_crs_required: true,
    standards_count: 4
  },
  
  // Extracted Technical Specifications with Evidence Chains
  extracted_requirements: [
    {
      id: "req-1",
      parameter: "Ingress Protection Rating",
      specified_value: "IP 66 Minimum (Optical & Driver Compartment)",
      category: "Environmental & Protection",
      status: "VALID",
      severity: "SUCCESS",
      compliance_status: "Fully Supported by IS 10322",
      evidence_chain: {
        standard_code: "IS 10322 (Part 5/Sec 3): 2012",
        standard_title: "Luminaires for Street and Highway Lighting",
        clause: "Clause 6.3 - Dust and Moisture Ingress Protection",
        quote: "Luminaires intended for outdoor roadway lighting shall have an ingress protection rating of not less than IP65 for optical assembly and IP65 for control gear. IP66 is acceptable for heavy-duty highway installations.",
        page_number: 14,
        confidence: 0.98,
        provenance_source: "BIS Official Standard Document (Reaffirmed 2022)"
      }
    },
    {
      id: "req-2",
      parameter: "Luminous Efficacy",
      specified_value: "≥ 130 lm/W",
      category: "Photometric Performance",
      status: "VALID",
      severity: "SUCCESS",
      compliance_status: "Meets & Exceeds Baseline IS Standard",
      evidence_chain: {
        standard_code: "IS 10322 (Part 5/Sec 3) & BEE Star Rating Scheme",
        standard_title: "Performance Requirements for Outdoor Luminaires",
        clause: "Clause 7.1 & BEE LED Luminaire Schedule 2023",
        quote: "System luminous efficacy for street lighting luminaires shall be minimum 100 lm/W (5-Star rating requires ≥ 120 lm/W). The specified 130 lm/W is compliant with high-efficiency procurement guidelines.",
        page_number: 18,
        confidence: 0.94,
        provenance_source: "BIS Standard + BEE Star Rating Gazette 2023"
      }
    },
    {
      id: "req-3",
      parameter: "Surge Protection Level",
      specified_value: "10 kV / 10 kA (External SPD)",
      category: "Electrical Safety",
      status: "VALID",
      severity: "SUCCESS",
      compliance_status: "Mandated for Indian Highway Grid Conditions",
      evidence_chain: {
        standard_code: "IS 16102 (Part 1): 2012 / Amd 2: 2021",
        standard_title: "Self-Ballasted LED Lamps / Control Gear Safety",
        clause: "Clause 12.4 - Transient Overvoltage Immunity",
        quote: "For outdoor luminaires installed in severe surge environments, an external Surge Protection Device (SPD) rated for at least 10 kV/10 kA tested as per IS/IEC 61643-11 shall be incorporated.",
        page_number: 22,
        confidence: 0.96,
        provenance_source: "BIS Amendment 2 (2021)"
      }
    },
    {
      id: "req-4",
      parameter: "Correlated Color Temperature (CCT)",
      specified_value: "Strictly 5700K ± 50K Only",
      category: "Optical & CCT",
      status: "RESTRICTIVE_FLAG",
      severity: "WARNING",
      compliance_status: "Excessively Restrictive Tolerance Window",
      issue_description: "Specifying CCT tolerance as narrow as ± 50K (5650K - 5750K) excludes standard BIS-certified LED chips (which allow ± 300K). This risks single-vendor lock-in.",
      evidence_chain: {
        standard_code: "IS 16102 (Part 2): 2012",
        standard_title: "Performance Requirements for LED Modules",
        clause: "Table 2 - Standard CCT Nominal Values & Chromaticity Tolerances",
        quote: "Nominal CCT 5700K allows chromaticity coordinates corresponding to 7-step MacAdam ellipse (tolerance range approximately ± 355K).",
        page_number: 9,
        confidence: 0.91,
        provenance_source: "IS 16102 Part 2 Specification"
      }
    },
    {
      id: "req-5",
      parameter: "BIS CRS Safety Registration",
      specified_value: "Mandatory BIS CRS Registration Mark on Luminaire & Driver",
      category: "Regulatory & Legal Compliance",
      status: "VALID",
      severity: "SUCCESS",
      compliance_status: "Mandatory Regulatory Requirement (QCO)",
      evidence_chain: {
        standard_code: "QCO S.O. 2021(E) / IS 10322 (Part 5/Sec 3)",
        standard_title: "Electrical Equipment Quality Control Order 2019",
        clause: "Section 3 - Prohibition of Manufacture/Import without BIS Mark",
        quote: "No person shall manufacture, import, distribute or sell LED luminaires for road lighting without carrying the Standard Mark under a license from BIS as per IS 10322 (Part 5/Sec 3).",
        page_number: 2,
        confidence: 0.99,
        provenance_source: "Ministry of Electronics & IT / MeitY QCO Order 2019"
      }
    },
    {
      id: "req-6",
      parameter: "Total Harmonic Distortion (THD)",
      specified_value: "THD ≤ 10%",
      category: "Electrical Performance",
      status: "VALID",
      severity: "SUCCESS",
      compliance_status: "Compliant with Power Quality Guidelines",
      evidence_chain: {
        standard_code: "IS 15885 (Part 2/Sec 13): 2012",
        standard_title: "AC or DC Supplied Electronic Control Gear for LED Modules",
        clause: "Clause 14.1 - Harmonics Current Limits",
        quote: "The total harmonic distortion (THD) of the input current shall not exceed 10% at rated voltage and full load.",
        page_number: 11,
        confidence: 0.93,
        provenance_source: "IS 15885 Part 2/Sec 13 Document"
      }
    },
    {
      id: "req-7",
      parameter: "Housing Material Specification",
      specified_value: "Die-Cast Aluminum ADC12 with Powder Coating",
      category: "Mechanical & Thermal",
      status: "MISSING_STANDARD_REF",
      severity: "INFO",
      compliance_status: "Common Practice - Missing Specific Indian Standard Citation",
      issue_description: "Tender specifies ADC12 material without citing IS 617 (Aluminum Casting Alloy standard). Adding IS 617 reference strengthens legal defensibility.",
      evidence_chain: {
        standard_code: "IS 617: 1994 (Reaffirmed 2020)",
        standard_title: "Aluminum and Aluminum Alloy Ingots and Castings for General Engineering Purposes",
        clause: "Grade Designation Alloy 4600 (ADC12 equivalent)",
        quote: "Castings shall conform to chemical composition limits of Cu 1.5-3.5% and Si 9.6-12.0%.",
        page_number: 6,
        confidence: 0.88,
        provenance_source: "BIS Material Specification Standards"
      }
    }
  ],

  // Mapped Standards Intelligence & Version Relationship Network
  standards_intelligence: [
    {
      id: "std-10322-5-3",
      code: "IS 10322 (Part 5/Sec 3)",
      title: "Luminaires - Particular Requirements - Luminaires for Street and Highway Lighting",
      current_version: "2012 (Reaffirmed 2022)",
      status: "CURRENT",
      status_badge: "CURRENT",
      is_qco_mandatory: true,
      amendments: [
        { code: "Amd 1", year: "2017", description: "Updated thermal test limits and IP testing procedures" },
        { code: "Amd 2", year: "2021", description: "Mandated higher surge immunity & driver encapsulation rules" }
      ],
      supersedes: "IS 2149: 1970 (Specification for Luminaires for Street Lighting)",
      normative_references: [
        "IS 10322 (Part 1): 2014 - General Requirements and Tests for Luminaires",
        "IS 15885 (Part 2/Sec 13): 2012 - Safety of LED Control Gear / Drivers",
        "IS 16102 (Part 1 & 2): 2012 - Self-Ballasted LED Lamps & Modules"
      ],
      international_equivalent: "IEC 60598-2-3 (2011) - Luminaires for road and street lighting (Identical adoption)",
      qco_details: {
        order_name: "Electrical Equipment (Quality Control) Order 2019",
        issuing_authority: "Department for Promotion of Industry and Internal Trade (DPIIT) / MeitY",
        effective_date: "2020-01-01",
        crs_mandatory: true
      }
    },
    {
      id: "std-16102-1",
      code: "IS 16102 (Part 1)",
      title: "Self-Ballasted LED Lamps for General Lighting Services - Safety Requirements",
      current_version: "2012 (Reaffirmed 2022)",
      status: "AMENDED",
      status_badge: "AMENDED",
      is_qco_mandatory: true,
      amendments: [
        { code: "Amd 1", year: "2015", description: "Flame retardant housing test addition" },
        { code: "Amd 2", year: "2019", description: "Cap safety torque requirements" }
      ],
      supersedes: "None (First edition created for LED lamps)",
      normative_references: [
        "IS 6863: 1973 - Methods of measurement of electrical properties",
        "IS 10322 (Part 1): 2014"
      ],
      international_equivalent: "IEC 62560: 2011",
      qco_details: {
        order_name: "Compulsory Registration Scheme (CRS) Phase II",
        issuing_authority: "MeitY",
        effective_date: "2015-09-13",
        crs_mandatory: true
      }
    },
    {
      id: "std-15885-2-13",
      code: "IS 15885 (Part 2/Sec 13)",
      title: "Lamp Control Gear - Particular Requirements for DC/AC Supplied Electronic Control Gear for LED Modules",
      current_version: "2012 (Reaffirmed 2020)",
      status: "CURRENT",
      status_badge: "CURRENT",
      is_qco_mandatory: true,
      amendments: [
        { code: "Amd 1", year: "2017", description: "Driver thermal overload protection testing" }
      ],
      supersedes: "IS 13021 (Part 2): 1991 (Ballasts for Tubular Fluorescent Lamps)",
      normative_references: [
        "IS 15885 (Part 1): 2011 - General Safety Requirements",
        "IS 14700 (Part 3/Sec 2): 2008 - Harmonic Current Emissions"
      ],
      international_equivalent: "IEC 61347-2-13: 2006",
      qco_details: {
        order_name: "Electronics & IT Goods (Compulsory Registration) Order",
        issuing_authority: "MeitY",
        effective_date: "2016-12-01",
        crs_mandatory: true
      }
    },
    {
      id: "std-2149-old",
      code: "IS 2149: 1970",
      title: "Specification for Luminaires for Street Lighting (Legacy Filament/HID standard)",
      current_version: "1970 (Withdrawn)",
      status: "SUPERSEDED",
      status_badge: "SUPERSEDED",
      is_qco_mandatory: false,
      amendments: [],
      supersedes: "None",
      normative_references: [],
      international_equivalent: "Deprecated",
      withdrawal_reason: "Withdrawn and completely replaced by IS 10322 (Part 5/Sec 3) for modern luminaires."
    }
  ],

  // Restrictiveness & Requirement Quality Analysis with Counterfactuals
  restrictiveness_analysis: {
    overall_assessment: "POTENTIALLY_RESTRICTIVE",
    flagged_count: 1,
    summary: "1 technical parameter contains an unnaturally narrow tolerance window that may restrict competitive bidding without technical justification.",
    counterfactuals: [
      {
        id: "cf-1",
        requirement_id: "req-4",
        parameter: "Correlated Color Temperature (CCT)",
        current_clause: "Strictly 5700K ± 50K Only",
        proposed_relaxation: "5700K (Nominal) as per IS 16102 (Part 2) standard chromaticity tolerance (± 300K)",
        why_flagged: "A 50K window is virtually impossible for LED phosphors without hand-sorting / custom binning, raising vendor bias concerns.",
        impact_analysis: {
          vendor_pool_expansion: "+45% wider supplier eligibility (allows major Indian manufacturers like Havells, Wipro, Bajaj, Surya)",
          standards_compliance: "100% compliant with IS 10322 (Part 5/Sec 3) & BEE 5-Star guidelines",
          mandatory_qco_impact: "No effect on QCO compliance (remains fully certified)",
          cost_saving_estimate: "Estimated 8-12% lower unit cost due to standard LED chip availability"
        }
      }
    ]
  },

  // Pre-Publication Defense & Dossier Scorecard
  pre_publication_summary: {
    scorecard: {
      completeness_score: 92, // out of 100
      defensibility_score: 88,
      regulatory_compliance_score: 100,
      vendor_neutrality_score: 75 // docked due to 5700K ± 50K clause
    },
    missing_recommendations: [
      {
        title: "Include IS 617 Reference for Aluminum Alloy Casting",
        description: "Adding explicit reference to IS 617 (Grade 4600 / ADC12) ensures structural durability compliance."
      },
      {
        title: "Specify IS 14700 (Part 3/Sec 2) for EMC / Harmonic Compliance",
        description: "Citing the exact EMC standard prevents electrical noise pollution on municipal grids."
      }
    ],
    defensibility_statement: "The technical requirements in this draft tender are 100% grounded in current Indian Standards (IS 10322 Part 5 Sec 3: 2012 Amd 2). Relaxing the CCT tolerance clause as recommended will ensure full audit compliance under CVC guidelines."
  }
};
