import json
import re
import html
from collections import defaultdict

def clean_title(title):
    if not title:
        return ""
    # Decode HTML
    c = html.unescape(title)
    # Remove accidental duplicated spaces
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
        'lighting': ['lighting', 'led', 'luminaire', 'lamp'],
        'electrical cable': ['cable', 'wire'],
        'transformer': ['transformer'],
        'motor': ['motor', 'rotating electrical machine'],
        'switchgear': ['switchgear', 'controlgear'],
        'appliance': ['household', 'appliance', 'refrigerator', 'oven', 'heater']
    }
    
    for cat, terms in mapping.items():
        if any(term in title_lower for term in terms):
            categories.add(cat)
            
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
        return 'Application Guide'
    if 'maintenance' in tl: 
        return 'Maintenance'
    if 'specification' in tl or 'requirements' in tl: 
        return 'Product Specification'
    return None

def process():
    with open('d:/ai_engine_SIH/data/standards.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []
    report = {
        "total_records": len(data),
        "records_cleaned": 0,
        "records_with_scope": 0,
        "records_with_validity_date": 0,
        "records_with_references": 0,
        "records_with_related_standards": 0,
        "records_with_test_methods": 0,
        "records_needing_verification": 0,
        "major_cleaning_operations": ["HTML decoding", "Spacing normalization", "Validity extraction", "Category inference", "Type inference"]
    }

    family_map = defaultdict(list)

    for rec in data:
        raw_rec = dict(rec)
        new_rec = {}
        new_rec['raw_record'] = raw_rec

        # 1. CLEAN EXISTING DATA
        new_rec['raw_is_number'] = rec.get('is_number')
        norm_is = normalize_is_number(new_rec['raw_is_number'])
        new_rec['normalized_is_number'] = norm_is
        new_rec['is_number'] = norm_is

        raw_title = rec.get('title', '')
        new_rec['raw_title'] = raw_title
        clean_t = clean_title(raw_title)

        # 4. VALIDITY DATE
        clean_t, valid_date = extract_validity(clean_t)
        new_rec['clean_title'] = clean_t
        new_rec['title'] = clean_t

        new_rec['valid_upto'] = valid_date if valid_date else rec.get('valid_upto')
        if new_rec['valid_upto']:
             report['records_with_validity_date'] += 1

        # keywords
        kws = rec.get('keywords', [])
        clean_kws = list(set([clean_title(k).title() for k in kws if k]))
        new_rec['keywords'] = clean_kws

        # 2. METADATA
        new_rec['edition_year'] = rec.get('year')
        new_rec['price'] = rec.get('price')
        new_rec['status'] = rec.get('status')
        new_rec['source'] = rec.get('source')

        # 3. VERSION HANDLING
        new_rec['version'] = {
            "record_edition": norm_is,
            "record_year": new_rec['edition_year'],
            "latest_known_version": None,
            "latest_known_year": None,
            "supersedes": rec.get('supersedes'),
            "superseded_by": rec.get('superseded_by'),
            "verification_status": "not_verified"
        }

        # 5. SCOPE
        sc = rec.get('scope')
        if not sc and clean_t:
            sc = "Standard relating to " + clean_t.lower()
        new_rec['scope'] = sc
        if sc: report['records_with_scope'] += 1

        # 6. PRODUCT CATEGORY
        new_rec['product_categories'] = infer_categories(clean_t, clean_kws)

        # 7. STANDARD TYPE
        new_rec['standard_type'] = infer_type(clean_t)

        # 8. NORMATIVE REFERENCES
        new_rec['normative_references'] = rec.get('normative_references', [])
        if new_rec['normative_references']: report['records_with_references'] += 1

        # 9. RELATED STANDARDS
        new_rec['related_standards'] = rec.get('related_standards', [])
        if new_rec['related_standards']: report['records_with_related_standards'] += 1

        # 10. TEST METHODS
        new_rec['test_methods'] = rec.get('test_methods', [])
        if new_rec['test_methods']: report['records_with_test_methods'] += 1

        # 11. CERTIFICATION
        old_cert = rec.get('certification_requirements', {})
        new_rec['certification'] = {
            "mandatory": None,
            "scheme": None,
            "qco": None,
            "verified": False,
            "notes": old_cert.get('details', "Not stated in source catalog; verify via BIS certification scheme lookup.")
        }
        report['records_needing_verification'] += 1

        # 12. SOURCE
        new_rec['source_info'] = {
            "organization": "BIS",
            "source_type": "BIS catalogue",
            "verified": False
        }

        # 13. SEARCH TEXT
        search_parts = [
            norm_is,
            clean_t,
            sc or "",
            " ".join(clean_kws),
            " ".join(new_rec['product_categories']),
            new_rec['standard_type'] or ""
        ]
        new_rec['search_text'] = " ".join([str(p) for p in search_parts if p])

        # 14. DATA QUALITY
        score = sum([
            1 if norm_is else 0,
            1 if clean_t else 0,
            1 if new_rec['edition_year'] else 0,
            1 if sc else 0,
            1 if clean_kws else 0,
            1 if new_rec['status'] else 0,
            1 
        ])
        new_rec['data_quality'] = {
            "completeness_score": score,
            "issues": [],
            "needs_verification": ["certification"]
        }

        family_map[norm_is].append(new_rec)
        cleaned_data.append(new_rec)
        report['records_cleaned'] += 1

    # Second pass: link versions
    for norm_is, items in family_map.items():
        if len(items) > 1:
            items.sort(key=lambda x: x['edition_year'] or 0, reverse=True)
            latest = items[0]
            for item in items:
                item['version']['latest_known_version'] = latest['normalized_is_number']
                item['version']['latest_known_year'] = latest['edition_year']

    with open('d:/ai_engine_SIH/cleaned_bis_standards.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4)

    with open('d:/ai_engine_SIH/data_cleaning_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)

if __name__ == '__main__':
    process()
