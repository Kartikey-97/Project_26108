import json
import re
import html
from collections import defaultdict
import os

def clean_title(title):
    if not title:
        return ""
    c = html.unescape(title)
    c = re.sub(r'\s+', ' ', c).strip()
    return c

def normalize_is_number(num):
    if not num:
        return ""
    c = re.sub(r'\s*:\s*', ': ', num)
    c = re.sub(r'\s+', ' ', c).strip()
    return c

def extract_validity(title):
    match = re.search(r'\(Vai?ld\s+upto\s+([^)]+)\)', title, re.IGNORECASE)
    if match:
        date_str = match.group(1)
        new_title = re.sub(r'\s*\(Vai?ld\s+upto\s+[^)]+\)', '', title, flags=re.IGNORECASE)
        return new_title.strip(), date_str.strip()
    return title, None

def infer_categories(title, keywords):
    categories = set()
    title_lower = title.lower()
    
    mapping = {
        'Lighting & LED': ['lighting', 'led', 'luminaire', 'lamp', 'street light', 'flood light'],
        'Electrical Installation & Safety': ['installation', 'wiring', 'safety', 'circuit breaker', 'earthing', 'switchgear'],
        'Motors & Rotating Machines': ['motor', 'rotating electrical machine', 'generator', 'turbine'],
        'Cables & Wires': ['cable', 'wire', 'conductor'],
        'Transformers': ['transformer', 'inductor'],
        'Batteries & Energy Storage': ['battery', 'batteries', 'energy storage', 'lithium-ion', 'accumulator'],
        'Medical Electrical Equipment': ['medical electrical', 'hospital', 'x-ray', 'incubator', 'surgical'],
        'Renewable Energy & EV': ['solar', 'photovoltaic', 'electric vehicle', 'ev supply', 'electric power train'],
        'Testing & Measurement': ['measurement', 'testing', 'meter', 'instrument']
    }
    
    for cat, terms in mapping.items():
        if any(term in title_lower for term in terms):
            categories.add(cat)
            
    if not categories:
        categories.add('General Electrical')
        
    return list(categories)

def infer_type(title):
    tl = title.lower()
    if 'test' in tl or 'determination' in tl or 'measurement' in tl or 'method' in tl: 
        return 'Testing Method'
    if 'safety' in tl: 
        return 'Safety'
    if 'performance' in tl: 
        return 'Performance'
    if 'installation' in tl: 
        return 'Installation'
    if 'design' in tl: 
        return 'Design'
    if 'vocabulary' in tl or 'terminology' in tl or 'definitions' in tl: 
        return 'Terminology'
    if 'guide' in tl or 'practice' in tl: 
        return 'Code of Practice'
    if 'specification' in tl or 'requirements' in tl: 
        return 'Product Specification'
    return 'verification_required'

def generate_keywords(title_lower, orig_keywords, cats):
    kws = set(orig_keywords)
    for c in cats:
        kws.add(c)
    if 'led' in title_lower: kws.add('LED')
    if 'street' in title_lower: kws.add('street lighting')
    if 'motor' in title_lower: kws.add('electric motor')
    if 'cable' in title_lower: kws.add('electrical cable')
    if 'transformer' in title_lower: kws.add('transformer')
    return list(kws)

def process():
    raw_path = 'data/bis_catalogue_raw.json'
    if not os.path.exists(raw_path):
        print("Raw file not found")
        return
        
    with open(raw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Gather stats
    total_records = len(data)
    records_with_validity_dates = 0
    records_with_amendments = 0
    records_with_scope = 0
    
    normalized_data = []
    
    for rec in data:
        raw_is = rec.get('is_number')
        norm_is = normalize_is_number(raw_is)
        raw_t = rec.get('title', '')
        ct = clean_title(raw_t)
        ct, valid = extract_validity(ct)
        
        if valid: records_with_validity_dates += 1
        if rec.get('scope'): records_with_scope += 1
        if rec.get('amendments'): records_with_amendments += 1
        
        rec['_norm_is'] = norm_is
        rec['_clean_t'] = ct
        rec['_valid'] = valid
        
        normalized_data.append(rec)
        
    family_map = defaultdict(list)
    for rec in normalized_data:
        family_map[rec['_norm_is']].append(rec)
        
    duplicate_families = sum(1 for k, v in family_map.items() if len(v) > 1)
    
    report = {
        "total_records": total_records,
        "duplicate_is_number_families": duplicate_families,
        "records_with_validity_dates": records_with_validity_dates,
        "records_with_amendments": records_with_amendments,
        "records_with_scope": records_with_scope,
        "records_needing_verification": total_records
    }
    
    with open('data/data_quality_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # SELECT 50 RECORDS
    # Let's prioritize families that have multiple editions to show version tracking, and pick varied categories.
    selected_families = []
    
    # Target categories from prompt
    target_topics = ['electrical equipment', 'lighting', 'led', 'street', 'safety', 'installation', 'testing', 'cable', 'transformer', 'motor', 'battery', 'solar', 'ev', 'vehicle', 'electronic']
    
    # Sort families to try and get good ones
    sorted_families = sorted(family_map.keys(), key=lambda k: len(family_map[k]), reverse=True)
    
    count = 0
    for fam in sorted_families:
        items = family_map[fam]
        items.sort(key=lambda x: x.get('year') or 0, reverse=True)
        latest_item = items[0]
        t = latest_item['_clean_t'].lower()
        
        # Keep if it matches a priority topic or if we just need more
        if any(topic in t for topic in target_topics) or count < 25:
            selected_families.append(fam)
            count += len(items)
        
        if count >= 50:
            break
            
    # Process the selected
    final_50 = []
    
    for fam in selected_families:
        items = family_map[fam]
        latest_year = items[0].get('year')
        latest_edition = fam
        
        for rec in items:
            clean_t = rec['_clean_t']
            valid_d = rec['_valid']
            cats = infer_categories(clean_t, [])
            stype = infer_type(clean_t)
            
            kws = rec.get('keywords', [])
            clean_kws = list(set([clean_title(k).title() for k in kws if k]))
            better_kws = generate_keywords(clean_t.lower(), clean_kws, cats)
            
            sc = rec.get('scope')
            scope_summary = None
            if not sc and clean_t:
                scope_summary = "Derived summary: " + clean_t
                
            # version
            ver = {
                "record_edition": fam,
                "record_year": rec.get('year'),
                "latest_known_edition": latest_edition if len(items) > 1 else None,
                "latest_known_year": latest_year if len(items) > 1 else None,
                "supersedes": rec.get('supersedes'),
                "superseded_by": rec.get('superseded_by'),
                "verification_status": "not_verified"
            }
            
            stat = rec.get('status')
            
            search_parts = [
                fam,
                clean_t,
                sc or scope_summary or "",
                " ".join(better_kws),
                " ".join(cats),
                stype
            ]
            search_text = " ".join([str(p) for p in search_parts if p])
            
            out_rec = {
                "is_number": rec.get('is_number'),
                "normalized_is_number": fam,
                "edition_year": rec.get('year'),
                "title": clean_t,
                "raw_title": rec.get('title'),
                "clean_title": clean_t,
                "price": rec.get('price', 0),
                "scope": sc,
                "scope_summary": scope_summary,
                "keywords": better_kws,
                "product_categories": cats,
                "standard_type": stype,
                "normative_references": [],
                "related_standards": [],
                "test_methods": [],
                "certification": {
                    "mandatory": None,
                    "scheme": None,
                    "qco": None,
                    "qco_effective_date": None,
                    "verified": False,
                    "source": None
                },
                "status": {
                    "value": stat,
                    "concurrent_running": True if stat == "Active (Concurrent)" else None,
                    "verified": False,
                    "source": "BIS"
                },
                "version": ver,
                "amendments": [],
                "valid_upto": valid_d,
                "search_text": search_text,
                "source": {
                    "organization": "BIS",
                    "source_type": "BIS standards catalogue",
                    "verified": False,
                    "url": None
                },
                "data_quality": {
                    "overall": "medium",
                    "verified_fields": [],
                    "unverified_fields": ["scope", "normative_references", "certification", "status", "amendments"],
                    "needs_manual_verification": ["certification", "status", "scope", "version"]
                },
                "raw_record": {k:v for k,v in rec.items() if not k.startswith('_')}
            }
            final_50.append(out_rec)
            
    with open('data/bis_50_knowledge_base.json', 'w', encoding='utf-8') as f:
        json.dump(final_50, f, indent=4)
        
    print(f"Generated data/bis_50_knowledge_base.json with {len(final_50)} records.")

    # Create demo queries
    queries = [
      {
        "query": "We need to procure LED street lights for highway roads.",
        "expected_category": "Lighting & LED"
      },
      {
        "query": "We need electrical safety standards for household appliances.",
        "expected_category": "Electrical Installation & Safety"
      },
      {
        "query": "We need to procure electric motors for industrial equipment.",
        "expected_category": "Motors & Rotating Machines"
      },
      {
        "query": "We need testing standards for medical equipment.",
        "expected_category": "Medical Electrical Equipment"
      },
      {
        "query": "We need standards for electrical cables used in buildings.",
        "expected_category": "Cables & Wires"
      }
    ]
    with open('data/demo_queries.json', 'w', encoding='utf-8') as f:
        json.dump(queries, f, indent=2)

if __name__ == '__main__':
    process()
