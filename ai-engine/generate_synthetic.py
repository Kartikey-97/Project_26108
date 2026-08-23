import json
import random
import os

# Ensure reproducibility
random.seed(42)

def generate_synthetic_data(input_file="data/bis_50_knowledge_base.json", output_file="data/ML_200_standards_dataset.json"):
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        standards = json.load(f)

    synthetic_dataset = []
    
    # Track statistics
    class_counts = {
        "TECHNICAL_SPECIFICATION": 0,
        "CERTIFICATION": 0,
        "TESTING": 0,
        "SAFETY": 0,
        "PERFORMANCE": 0,
        "MATERIAL": 0,
        "INSTALLATION": 0
    }
    
    def add_req(text, req_type, std_id):
        synthetic_dataset.append({
            "id": f"synth_{len(synthetic_dataset)+1:04d}",
            "requirement_text": text,
            "requirement_type": req_type,
            "source_standard_id": std_id,
            "source": "synthetic_from_bis_metadata"
        })
        class_counts[req_type] += 1

    for std in standards:
        is_num = std.get('is_number', '')
        title = std.get('title', '')
        keywords = std.get('keywords', [])
        categories = std.get('product_categories', [])
        test_methods = std.get('test_methods', [])
        cert = std.get('certification', {})
        scope = std.get('scope', '')
        std_type = std.get('standard_type', '')

        if not is_num or not title:
            continue

        # 1. TECHNICAL_SPECIFICATION (Base generation on title and keywords)
        kw = random.choice(keywords) if keywords else "product"
        cat = random.choice(categories) if categories else "material"
        
        templates_tech = [
            f"The {kw.lower()} must conform to {is_num} requirements.",
            f"Supply {cat.lower()} strictly as per {is_num}.",
            f"All {kw.lower()} items should meet the specification of {is_num}.",
            f"The {cat.lower()} used in the project must comply with {is_num}.",
            f"Technical compliance with {is_num} is mandatory for the {kw.lower()}."
        ]
        # pick 3 tech specs
        for t in random.sample(templates_tech, min(3, len(templates_tech))):
            add_req(t, "TECHNICAL_SPECIFICATION", is_num)

        # 2. CERTIFICATION
        if cert.get('mandatory') or str(cert.get('scheme')).lower() in ['isi mark', 'crs']:
            scheme = cert.get('scheme') or "BIS certification"
            templates_cert = [
                f"The product must hold a valid {scheme} registration under {is_num}.",
                f"Supplier must furnish a valid {scheme} license for {is_num}.",
                f"Mandatory {scheme} is required as per Quality Control Order for {is_num}."
            ]
            for t in templates_cert:
                add_req(t, "CERTIFICATION", is_num)

        # 3. TESTING
        if test_methods:
            for tm in test_methods:
                templates_test = [
                    f"A type test report for {tm} per {is_num} must be submitted.",
                    f"The {kw.lower()} shall be tested for {tm} according to {is_num}.",
                    f"Testing for {tm} shall be performed as outlined in {is_num}."
                ]
                add_req(random.choice(templates_test), "TESTING", is_num)
        else:
            # If standard type implies testing
            if "test" in title.lower() or "method" in title.lower():
                add_req(f"Testing procedures must follow the guidelines stated in {is_num} ({title}).", "TESTING", is_num)

        # 4. SAFETY
        if "safety" in title.lower() or "safety" in (std_type or "").lower() or any("safety" in k.lower() for k in keywords):
            templates_safety = [
                f"Safety requirements for the {kw.lower()} must meet {is_num}.",
                f"The {cat.lower()} shall ensure basic safety according to {is_num}.",
                f"Electrical safety must be guaranteed as per {is_num} standard."
            ]
            for t in random.sample(templates_safety, 2):
                add_req(t, "SAFETY", is_num)

        # 5. PERFORMANCE
        if "performance" in title.lower() or "efficacy" in (scope or "").lower() or "efficiency" in title.lower():
            add_req(f"Performance criteria must adhere to {is_num}.", "PERFORMANCE", is_num)
            add_req(f"The {kw.lower()} shall meet the performance parameters defined in {is_num}.", "PERFORMANCE", is_num)

        # 6. MATERIAL
        if "steel" in title.lower() or "aluminium" in title.lower() or "pvc" in title.lower() or "material" in (scope or "").lower():
            add_req(f"The material composition shall strictly conform to {is_num}.", "MATERIAL", is_num)
            add_req(f"Raw materials used must be tested as per {is_num}.", "MATERIAL", is_num)

        # 7. INSTALLATION
        if "installation" in title.lower() or "practice" in title.lower() or "code" in title.lower():
            add_req(f"Installation works shall be carried out according to the code of practice in {is_num}.", "INSTALLATION", is_num)
            add_req(f"The contractor must follow {is_num} for erection and installation.", "INSTALLATION", is_num)

    # Output dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(synthetic_dataset, f, indent=2)

    # Train / Validation / Test split by source_standard_id to prevent leakage
    standard_ids = list(set([r['source_standard_id'] for r in synthetic_dataset]))
    random.shuffle(standard_ids)
    
    n_train = int(len(standard_ids) * 0.70)
    n_val = int(len(standard_ids) * 0.15)
    
    train_stds = set(standard_ids[:n_train])
    val_stds = set(standard_ids[n_train:n_train+n_val])
    test_stds = set(standard_ids[n_train+n_val:])
    
    train_count = sum(1 for r in synthetic_dataset if r['source_standard_id'] in train_stds)
    val_count = sum(1 for r in synthetic_dataset if r['source_standard_id'] in val_stds)
    test_count = sum(1 for r in synthetic_dataset if r['source_standard_id'] in test_stds)

    # Generate Report
    report = f"""# Synthetic Dataset Report

> **WARNING:** Training data is synthetic/weakly supervised and should be replaced by expert-labeled real procurement requirements for production deployment.

## Overview
- **Total Examples:** {len(synthetic_dataset)}
- **Number of Source Standards Used:** {len(standard_ids)}
- **Number of Classes:** {sum(1 for c in class_counts.values() if c > 0)}
- **Source Files Used:** `data/bis_50_knowledge_base.json`

## Class Distribution
"""
    for k, v in class_counts.items():
        if v > 0:
            report += f"- **{k}**: {v} examples\n"
            
    report += f"""
## Train/Validation/Test Split (Group-Aware)
To prevent data leakage, the split was performed at the `source_standard_id` level rather than the requirement level. This ensures that synthetic variations of the same standard are never seen in both train and test.

- **Train (70%)**: {len(train_stds)} standards → {train_count} examples
- **Validation (15%)**: {len(val_stds)} standards → {val_count} examples
- **Test (15%)**: {len(test_stds)} standards → {test_count} examples

## Limitations
- Extracted purely via simple templating from factual BIS attributes.
- Does not cover complex ambiguity found in real-world PDF tenders.
- Evaluates ability of models to associate procurement text with requirement categories within a clean boundary.
"""
    
    with open('data/ML_DATASET_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"Successfully generated {len(synthetic_dataset)} synthetic records.")
    print("Saved to data/ML_200_standards_dataset.json and data/ML_DATASET_REPORT.md")

if __name__ == "__main__":
    generate_synthetic_data()
