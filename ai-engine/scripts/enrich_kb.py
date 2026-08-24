"""
ai-engine/scripts/enrich_kb.py

Comprehensive knowledge-base enrichment pipeline.
Runs entirely on stdlib + the existing JSON files — no ML packages needed.
"""

import json
import re
import os
from collections import defaultdict

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(SCRIPT_DIR, '..', 'data')

FULL_KB    = os.path.join(DATA_DIR, 'bis_full_knowledge_base.json')
CURATED    = os.path.join(DATA_DIR, 'curated_additions.json')
RAW_CAT    = os.path.join(DATA_DIR, 'standards.json')
OUTPUT     = FULL_KB

# ─── Helpers ──────────────────────────────────────────────────────────────────

def norm_is(s: str) -> str:
    """Canonical key: uppercase, collapse whitespace, strip trailing spaces."""
    return re.sub(r'\s+', ' ', (s or '').upper().strip())

def is_number_variants(is_num: str) -> list:
    if not is_num: return []
    raw = is_num.strip()
    variants = {raw}

    m = re.search(r'\d[\d\s:\.]+', raw)
    if m:
        numeric = m.group().strip().rstrip(':')
        variants.add(numeric)
        no_space = re.sub(r'[\s:]+', '', numeric)
        if no_space: variants.add(no_space)
        base_m = re.match(r'(\d+)', numeric.replace(' ', ''))
        if base_m:
            base_num = base_m.group(1)
            variants.add('IS ' + base_num)
            variants.add('IS' + base_num)
            variants.add(base_num)

    no_colon = re.sub(r'\s*:\s*', ' ', raw).strip()
    variants.add(no_colon)
    no_space_all = re.sub(r'[\s:]+', '', raw)
    variants.add(no_space_all)

    return [v for v in variants if v and len(v) >= 2]

def extract_year_from_latest_version(latest_version: str):
    if not latest_version: return None
    m = re.search(r':(\d{4})\s*$', latest_version.strip())
    if m:
        y = int(m.group(1))
        if 1900 < y <= 2030: return y
    return None

# ─── Domain thesaurus ─────────────────────────────────────────────────────────
THESAURUS = [
    (["led road", "led street", "road luminaire", "street luminaire"], "led street light outdoor luminaire fixture highway street lighting road lighting municipal infrastructure energy efficient lumen lm/W watt IP66 CCT correlated colour temperature CRI colour rendering index lumen maintenance L70 L80 photometric efficacy BIS mandatory CRS procurement"),
    (["luminaire", "floodlight", "flood light", "high mast", "lumen output", "street lighting", "road lighting", "outdoor light"], "led street light outdoor luminaire fixture lighting energy efficient lumen photometric IP66 ingress protection watt CCT BIS CRS"),
    (["led lamp", "led bulb", "self ballasted"], "LED lamp LED bulb energy saving lamp general lighting BIS mandatory indoor LED"),
    (["general lighting", "light emitting diode", "led module", "led driver"], "LED lighting energy efficient lumen watt lm/W driver module"),
    (["lamp cap", "lamp holder", "lamp fitting", "lighting fitting"], "light fitting lamp holder socket luminaire component"),
    (["energy efficient", "induction motor", "squirrel cage"], "energy efficient motor IE1 IE2 IE3 IE4 efficiency class three phase motor BIS mandatory QCO procurement kW HP horsepower torque RPM speed"),
    (["rotating electrical machine", "rotating machine"], "electric motor induction motor synchronous motor generator alternator three phase motor single phase motor IE efficiency class kW HP torque RPM"),
    (["stepping motor", "stepper motor", "servo motor", "dc motor", "pm motor"], "motor servo stepper DC motor control positioning"),
    (["xlpe", "cross linked polyethylene", "cross-linked polyethylene"], "XLPE cable HV high voltage underground cable power transmission armoured sheathed cable HT cable 11kV 33kV 66kV 132kV medium voltage EHV"),
    (["pvc insulated", "pvc cable", "pvc sheathed"], "PVC cable electrical cable wiring conductor copper aluminium house wiring building wiring LV low voltage 1100V"),
    (["optical fibre", "optical fiber", "fibre cable"], "optical fibre cable communication cable data cable telecom broadband"),
    (["coaxial cable"], "coaxial cable RF cable communication cable antenna feeder"),
    (["winding wire", "enamelled wire", "winding copper"], "winding wire magnet wire enamelled conductor motor winding transformer winding"),
    (["cable tie", "cable management", "cable tray", "cable duct"], "cable management trunking tray duct installation accessories"),
    (["power transformer", "distribution transformer"], "power transformer distribution transformer step-up step-down KVA MVA oil-immersed winding losses efficiency voltage ratio"),
    (["dry-type transformer", "dry type transformer", "cast resin transformer"], "dry type transformer air cooled cast resin indoor installation KVA"),
    (["instrument transformer", "current transformer", "voltage transformer", "ct/pt"], "instrument transformer CT PT current transformer voltage transformer metering protection"),
    (["circuit breaker", "air circuit breaker", "acb", "vacuum circuit breaker", "vcb"], "circuit breaker ACB VCB switchgear protection interrupting capacity kA rated current"),
    (["miniature circuit breaker", "mcb"], "MCB miniature circuit breaker domestic wiring protection overload fault"),
    (["moulded case circuit breaker", "mccb"], "MCCB moulded case circuit breaker industrial protection overload"),
    (["residual current", "rccb", "rcd", "earth leakage"], "RCCB RCD earth leakage protection shock protection residual current device"),
    (["switchgear", "switchboard", "controlgear", "control gear"], "switchgear switchboard panel board LV MV distribution protection control"),
    (["motor control centre", "motor starter", "soft starter", "vfd", "variable frequency"], "motor control MCC variable frequency drive VFD soft starter DOL star delta"),
    (["surge protection", "surge arrester", "lightning arrester"], "surge protection SPD lightning arrester surge arrester overvoltage protection"),
    (["watt-hour meter", "watt hour meter", "energy meter", "kwh meter"], "energy meter electricity meter watt-hour meter kWh meter smart meter metering accuracy class BIS mandatory"),
    (["measuring instrument", "ammeter", "voltmeter", "wattmeter", "panel meter", "switchboard instrument"], "measuring instrument ammeter voltmeter wattmeter power factor meter frequency meter accuracy class panel meter"),
    (["household and similar electrical appliances", "household appliance", "domestic appliance"], "home appliance domestic appliance consumer electronics BIS mandatory CRS iron kettle mixer grinder fan heater toaster oven washing machine"),
    (["vacuum cleaner"], "vacuum cleaner household appliance floor care BIS mandatory"),
    (["microwave", "oven", "range hood", "exhaust fan"], "microwave oven cooking appliance kitchen appliance BIS mandatory"),
    (["air conditioner", "air conditioning", "heat pump", "room ac"], "air conditioner AC room cooler heat pump BEE star energy efficient"),
    (["refrigerator", "freezer", "cold storage"], "refrigerator freezer cooling appliance BEE star BIS mandatory"),
    (["water heater", "geyser", "immersion heater"], "water heater geyser immersion heater BIS mandatory household appliance"),
    (["medical electrical equipment", "medical device"], "medical device hospital equipment patient safety biomedical clinical IEC 60601 equivalent safety standard"),
    (["diagnostic", "patient monitoring", "defibrillator", "electrosurgical", "infusion pump", "syringe pump"], "medical equipment hospital clinical diagnostic patient care BIS standard"),
    (["personal protective equipment", "ppe", "safety helmet", "hard hat", "safety harness", "eye protection", "respiratory protection"], "PPE personal protective equipment safety BIS mandatory certification worker safety"),
    (["fire extinguisher", "fire fighting", "fire alarm", "fire detection"], "fire safety fire extinguisher fire alarm fire suppression BIS mandatory"),
    (["automobile", "automotive", "vehicle", "two-wheeler", "three-wheeler", "tyre", "tire"], "vehicle automobile car truck bus automotive tyre BIS mandatory CRS"),
    (["lpg", "liquefied petroleum gas", "gas cylinder", "pressure cylinder", "cng", "compressed natural gas"], "gas cylinder LPG CNG pressure vessel gas appliance BIS mandatory"),
    (["earthing", "grounding", "earth electrode"], "earthing grounding earth electrode earth pit electrical safety bonding LV MV"),
    (["wiring", "electrical installation", "conduit", "trunking", "cable tray", "socket outlet", "plug", "socket"], "electrical installation wiring conduit socket outlet plug BIS certification"),
    (["photovoltaic", "solar pv", "solar module", "solar cell", "solar panel", "solar inverter"], "solar photovoltaic PV panel module inverter renewable energy solar energy BIS mandatory certification"),
    (["wind turbine", "wind energy", "wind generator"], "wind turbine wind energy generator renewable energy"),
    (["pump", "centrifugal pump", "submersible pump", "reciprocating pump"], "pump centrifugal pump submersible pump water supply industrial pump BIS"),
    (["valve", "ball valve", "gate valve", "butterfly valve", "check valve"], "valve pipeline fitting fluid control water supply"),
    (["boiler", "pressure vessel", "steam"], "boiler pressure vessel steam industrial process plant"),
    (["information technology", "computer", "it equipment", "server", "networking", "router", "switch"], "information technology IT equipment computer server networking BIS standard"),
    (["telecommunication", "telecom", "modem", "telephone"], "telecom telecommunication communication equipment BIS standard"),
    (["cement", "concrete", "ready mixed", "ready-mixed"], "cement concrete building construction civil BIS mandatory CRS"),
    (["steel", "reinforcement", "rebar", "structural steel"], "steel reinforcement bar rebar structural steel building BIS mandatory"),
    (["brick", "tile", "ceramic", "flooring"], "brick tile ceramic flooring building material construction BIS"),
    (["paint", "varnish", "enamel", "lacquer"], "paint coating enamel protective coating BIS mandatory"),
    (["lubricant", "oil", "grease", "hydraulic fluid"], "lubricant oil grease industrial lubricant"),
    (["graphical symbol", "symbol for", "safety sign", "marking"], "symbol marking sign standard notation diagram"),
    (["test method", "methods of test", "methods of measurement", "testing of", "test procedure"], "test method measurement procedure testing standard laboratory"),
]

def apply_thesaurus(title: str) -> str:
    t_lower = title.lower()
    extra = []
    for triggers, terms in THESAURUS:
        if any(trig.lower() in t_lower for trig in triggers):
            extra.append(terms)
    return ' '.join(extra)

def application_context(title: str) -> str:
    t = title.lower()
    ctx = []
    if any(k in t for k in ['ship', 'marine', 'vessel', 'offshore']): ctx.append('marine naval offshore shipboard')
    if any(k in t for k in ['aircraft', 'aerospace', 'avionics']): ctx.append('aircraft aerospace aviation')
    if any(k in t for k in ['mine', 'mining', 'coal', 'underground mine']): ctx.append('mine mining underground hazardous area')
    if any(k in t for k in ['railway', 'rail', 'metro', 'traction']): ctx.append('railway rail traction metro transit')
    if any(k in t for k in ['hospital', 'medical', 'clinic', 'patient']): ctx.append('hospital medical healthcare clinical')
    if any(k in t for k in ['industrial', 'factory', 'plant', 'process']): ctx.append('industrial factory plant manufacturing process')
    if any(k in t for k in ['domestic', 'household', 'home', 'residential']): ctx.append('domestic residential home consumer')
    if any(k in t for k in ['outdoor', 'street', 'road', 'highway', 'municipal']): ctx.append('outdoor municipal infrastructure road highway')
    if any(k in t for k in ['hazardous', 'explosive atmosphere', 'flameproof', 'atex']): ctx.append('hazardous area explosive atmosphere Zone 1 Zone 2 ATEX')
    return ' '.join(ctx)

# ─── Category classification ──────────────────────────────────────────────────
CATEGORY_RULES = [
    (["led road", "led street", "road luminaire", "street luminaire", "is 16107", "16107"], "Lighting & LED"),
    (["luminaire", "floodlight", "high mast", "led lamp", "led bulb", "self ballasted", "lumen output", "led module", "light emitting diode", "is 10322", "10322", "is 16101", "16101", "is 15885", "15885", "street lighting", "is 1944", "1944"], "Lighting & LED"),
    (["solar pv", "photovoltaic", "solar cell", "solar module", "solar panel", "solar inverter", "wind turbine", "renewable energy"], "Renewable Energy"),
    (["medical electrical", "medical device", "clinical", "patient monitoring", "defibrillator", "infusion pump", "electrosurgical", "diagnostic imaging", "hospital equipment"], "Medical Electrical Equipment"),
    (["energy efficient induction motor", "squirrel cage motor", "is 12615", "12615"], "Motors & Rotating Machines"),
    (["rotating electrical machine", "induction motor", "synchronous motor", "dc motor", "servo motor", "stepper motor", "fractional horsepower", "motor winding", "is 4722", "4722", "is 15999", "15999", "is/iec 60034"], "Motors & Rotating Machines"),
    (["pvc insulated cable", "xlpe cable", "cross linked polyethylene", "winding wire", "enamelled wire", "optical fibre cable", "coaxial cable", "house wiring cable", "power cable", "armoured cable", "is 694", "694", "is 1554", "1554", "is 7098", "7098"], "Cables & Wires"),
    (["power transformer", "distribution transformer", "instrument transformer", "current transformer", "voltage transformer", "dry-type transformer", "circuit breaker", "switchgear", "switchboard", "controlgear", "motor control centre", "motor starter", "surge arrester", "is 2026", "2026", "is 11171", "11171", "is 8623", "8623", "is 4237"], "Power Equipment"),
    (["pump", "centrifugal pump", "submersible pump", "valve", "boiler", "compressor", "pressure vessel", "pipeline"], "Pumps & Fluid Equipment"),
    (["personal protective equipment", "ppe", "safety helmet", "hard hat", "safety harness", "fire extinguisher", "fire alarm"], "Safety Equipment"),
    (["cement", "concrete", "reinforcement", "structural steel", "rebar", "brick", "tile", "plywood", "building material"], "Civil & Construction Materials"),
    (["food", "beverage", "edible oil", "grain", "cereal", "milk", "dairy", "spice", "drinking water", "potable water", "agriculture", "fertilizer", "pesticide"], "Food & Agriculture"),
    (["textile", "fibre", "fabric", "yarn", "wool", "cotton", "silk", "man-made fibre", "technical textile"], "Textiles"),
    (["paint", "varnish", "enamel", "coating", "adhesive", "sealant", "lubricant", "grease"], "Chemicals & Coatings"),
    (["fastener", "bolt", "nut", "screw", "bearing", "gear", "spring", "chain", "forging", "casting"], "Mechanical Components"),
    (["gas cylinder", "lpg", "cng", "acetylene", "pressure regulator", "gas appliance", "gas meter"], "Gas & Pressure Equipment"),
    (["automobile", "vehicle", "tyre", "tire", "automotive", "two-wheeler", "three-wheeler", "engine emission"], "Automotive"),
    (["information technology", "computer", "it equipment", "telecommunication", "telecom", "modem", "router", "server"], "IT & Telecom"),
    (["furniture", "chair", "table", "desk", "cabinet", "office furniture", "steel furniture"], "Furniture"),
    (["water supply", "sanitation", "plumbing", "sewage", "effluent", "water treatment", "drinking water system", "wastewater"], "Water & Sanitation"),
    (["packaging", "container", "drum", "carton", "corrugated"], "Packaging"),
    (["wiring", "socket outlet", "plug", "energy meter", "earthing", "surge protection", "switchboard", "distribution board", "watt-hour meter", "measuring instrument"], "Electrical Installation & Safety"),
]

def infer_categories(title: str, is_number: str) -> list:
    text = (title + ' ' + is_number).lower()
    cats = []
    for triggers, cat in CATEGORY_RULES:
        if any(t.lower() in text for t in triggers):
            if cat not in cats: cats.append(cat)
            if len(cats) >= 3: break
    return cats or ["General Standards"]

def infer_std_type(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ['safety requirement', 'safe use', 'safety standard', 'safety of household', 'safety of machinery']): return 'Safety'
    if any(k in t for k in ['test method', 'methods of test', 'method of measurement', 'testing of', 'measurement of']): return 'Testing'
    if any(k in t for k in ['code of practice', 'installation guide', 'guide for', 'handbook', 'recommended practice']): return 'Code of Practice'
    if any(k in t for k in ['glossary', 'terminology', 'vocabulary', 'definition', 'terms and definitions']): return 'Glossary'
    if any(k in t for k in ['graphical symbol', 'symbols for', 'marking', 'designation of', 'classification of']): return 'Symbols & Markings'
    if any(k in t for k in ['installation', 'wiring', 'erection']): return 'Installation'
    return 'Specification'

def synthesise_scope(title: str, keywords: list, cats: list) -> str:
    base = re.sub(r'\s*[:-]\s*Part \d+[\w\s]*$', '', title, flags=re.IGNORECASE).strip()
    base = re.sub(r'\s*[:-]\s*Section \d+[\w\s]*$', '', base, flags=re.IGNORECASE).strip()
    cat_str = ', '.join(cats) if cats else 'General'
    if base.lower() == title.lower(): return f"{title}. Applicable to {cat_str} applications."
    return f"{base} — covers requirements for {cat_str} applications."

def build_search_text(rec: dict, cats: list, std_type: str, extra_terms: str) -> str:
    is_num = rec.get('is_number', '')
    title  = rec.get('title', '')
    scope  = rec.get('scope') or ''
    scope_s = rec.get('scope_summary', '') or ''
    kws    = ' '.join(rec.get('keywords') or [])
    year   = rec.get('edition_year') or rec.get('version', {}).get('record_year') or ''
    num_variants = ' '.join(is_number_variants(is_num))

    parts = [
        num_variants, title, scope[:300] if scope else '', scope_s[:200] if scope_s else '',
        kws, ' '.join(cats), std_type, extra_terms, application_context(title), str(year) if year else ''
    ]
    seen = set()
    words = []
    for part in parts:
        for w in part.split():
            lw = w.lower()
            if lw not in seen and len(w) >= 2:
                seen.add(lw)
                words.append(w)
    return ' '.join(words)

# ─── Main enrichment ──────────────────────────────────────────────────────────

def enrich(rec: dict, raw_lookup: dict) -> dict:
    is_num = rec.get('is_number', '')
    title  = rec.get('title', '') or ''
    raw    = raw_lookup.get(norm_is(is_num))

    # Year extraction
    latest_v = (raw or {}).get('latest_version') if raw else None
    extracted_year = extract_year_from_latest_version(latest_v)
    v = rec.setdefault('version', {})
    if extracted_year and (not v.get('latest_known_year') or v.get('latest_known_year') == v.get('record_year')):
        v['latest_known_year'] = extracted_year
    if rec.get('edition_year') and not v.get('record_year'):
        v['record_year'] = rec['edition_year']

    # Verification status
    st = rec.get('status', {})
    if isinstance(st, dict):
        status_val = st.get('value', 'Active')
    else:
        status_val = str(st)
        rec['status'] = {'value': status_val, 'verified': False, 'source': 'BIS'}
        st = rec['status']

    current_verif = v.get('verification_status', 'not_verified')
    if current_verif == 'not_verified' and 'Active' in status_val:
        v['verification_status'] = 'partial'

    # Scope synthesis
    cats     = infer_categories(title, is_num)
    std_type = infer_std_type(title)
    rec['product_categories'] = cats
    rec['standard_type']      = std_type

    if not rec.get('scope') or 'Derived summary' in (rec.get('scope_summary') or ''):
        rec['scope_summary'] = synthesise_scope(title, rec.get('keywords', []), cats)

    # Search text
    extra = apply_thesaurus(title)
    rec['search_text'] = build_search_text(rec, cats, std_type, extra)

    return rec

# ─── Load + merge ─────────────────────────────────────────────────────────────

print("Loading full knowledge base…")
with open(FULL_KB, encoding='utf-8') as f: full_kb = json.load(f)
print("Loading curated additions…")
with open(CURATED, encoding='utf-8') as f: curated = json.load(f)
print("Loading raw catalogue…")
with open(RAW_CAT, encoding='utf-8') as f: raw_records = json.load(f)

raw_lookup = {norm_is(r['is_number']): r for r in raw_records}
full_index = {norm_is(r['is_number']): r for r in full_kb}

added = 0
for r in curated:
    key = norm_is(r['is_number'])
    if key not in full_index:
        full_index[key] = r
        added += 1
    else:
        existing = full_index[key]
        if r.get('scope') and not existing.get('scope'): existing['scope'] = r['scope']
        if r.get('scope_summary') and 'Derived summary' not in r.get('scope_summary', ''): existing['scope_summary'] = r['scope_summary']
        if r.get('certification', {}).get('mandatory') is not None: existing['certification'] = r['certification']
        if r.get('test_methods'): existing['test_methods'] = r['test_methods']
        if r.get('related_standards'): existing['related_standards'] = r['related_standards']

print(f"Added {added} new standards from curated additions")

all_records = list(full_index.values())
print(f"Enriching {len(all_records)} records…")
enriched = [enrich(r, raw_lookup) for r in all_records]

from collections import Counter
cat_counts, type_counts, verif_counts = Counter(), Counter(), Counter()
scope_ok, avg_len = 0, 0

for r in enriched:
    for c in r.get('product_categories', []): cat_counts[c] += 1
    type_counts[r.get('standard_type', 'Unknown')] += 1
    verif_counts[r.get('version', {}).get('verification_status', 'unknown')] += 1
    if r.get('scope'): scope_ok += 1
    avg_len += len(r.get('search_text', ''))

avg_len //= len(enriched)

print(f"\nENRICHMENT COMPLETE — {len(enriched)} standards")
print(f"  Scope text available: {scope_ok}/{len(enriched)} ({100*scope_ok//len(enriched)}%)")
print(f"  Avg search_text length: {avg_len} chars")

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)
print(f"\nSaved to {OUTPUT}")
