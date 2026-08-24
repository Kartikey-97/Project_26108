# Synthetic Dataset Report

> **WARNING:** Training data is synthetic/weakly supervised and should be replaced by expert-labeled real procurement requirements for production deployment.

## Overview
- **Total Examples:** 260
- **Number of Source Standards Used:** 41
- **Number of Classes:** 6
- **Source Files Used:** `data/bis_50_knowledge_base.json`

## Class Distribution
- **TECHNICAL_SPECIFICATION**: 150 examples
- **CERTIFICATION**: 15 examples
- **TESTING**: 5 examples
- **SAFETY**: 66 examples
- **PERFORMANCE**: 4 examples
- **INSTALLATION**: 20 examples

## Train/Validation/Test Split (Group-Aware)
To prevent data leakage, the split was performed at the `source_standard_id` level rather than the requirement level. This ensures that synthetic variations of the same standard are never seen in both train and test.

- **Train (70%)**: 28 standards → 179 examples
- **Validation (15%)**: 6 standards → 36 examples
- **Test (15%)**: 7 standards → 45 examples

## Limitations
- Extracted purely via simple templating from factual BIS attributes.
- Does not cover complex ambiguity found in real-world PDF tenders.
- Evaluates ability of models to associate procurement text with requirement categories within a clean boundary.
