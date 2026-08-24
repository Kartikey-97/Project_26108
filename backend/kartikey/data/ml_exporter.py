"""
kartikey/data/ml_exporter.py

The ML Export — ETL Step 3 (final).

Takes the merged BIS+QCO unified records, generates a rich `semantic_text`
field for each standard, runs them through Kshiraj's EmbeddingService
(BAAI/bge-small-en-v1.5, 384-dim), and exports ml_ready_vectors.json.

This file is handed directly to Krishna to upsert into his Qdrant Vector DB.

semantic_text formula:
    "{designation}: {title}. Scope: {scope}. "
    "Normative references: {refs}. "
    "Domain keywords: {keywords}. "
    "QCO certification status: {mandatory/not mandatory}. "
    "Ministry: {ministry}. Products covered: {products}."

Output format (ml_ready_vectors.json):
    [
      {
        "id": "IS 732:2019",
        "is_number": "IS 732",
        "year": 2019,
        "title": "Code of Practice for Electrical Wiring Installations",
        "semantic_text": "IS 732:2019: Code of Practice ...",
        "embedding": [0.021, -0.031, ...],
        "embedding_dim": 384,
        "metadata": {
          "status": "active",
          "qco_notified": true,
          "qco_gazette_so_number": "S.O. 5147(E)",
          ...
        }
      }
    ]

Run directly:
    python -m kartikey.data.ml_exporter
    python -m kartikey.data.ml_exporter --output path/to/ml_ready_vectors.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
_BACKEND_ROOT = _HERE.parent.parent
_DEFAULT_BIS_INPUT = _BACKEND_ROOT / "shared" / "standards_dataset.json"
_DEFAULT_QCO_INPUT = _HERE / "mock_qco_database.json"
_DEFAULT_OUTPUT = _HERE / "ml_ready_vectors.json"

# ---------------------------------------------------------------------------
# semantic_text builder
# ---------------------------------------------------------------------------


def build_semantic_text(record: dict[str, Any]) -> str:
    """
    Stitch all meaningful text fields into a single rich paragraph that
    captures the full semantic content of the standard for embedding.

    The goal is maximum information density — the embedding model will
    learn a 384-dim vector that encodes ALL of:
      - the standard number and year
      - its title
      - its scope (what it covers and excludes)
      - normative references (related standards ecosystem)
      - domain keywords
      - mandatory QCO status and which products it applies to
    """
    parts: list[str] = []

    # 1. Canonical designation + title
    is_number = str(record.get("is_number", "")).strip()
    year = record.get("year")
    title = str(record.get("title", "")).strip()
    designation = f"{is_number}:{year}" if year else is_number
    parts.append(f"{designation}: {title}.")

    # 2. Scope (this is the meat — should now always be non-null after ingestor)
    scope = str(record.get("scope", "") or "").strip()
    if scope:
        parts.append(f"Scope: {scope}")

    # 3. Normative references
    refs = record.get("normative_references") or []
    if refs:
        refs_str = ", ".join(str(r) for r in refs)
        parts.append(f"Normative references: {refs_str}.")

    # 4. Domain keywords from BIS metadata
    keywords = record.get("keywords") or []
    if keywords:
        kw_str = ", ".join(str(k) for k in keywords[:10])  # cap at 10
        parts.append(f"Domain keywords: {kw_str}.")

    # 5. QCO / certification status
    qco_notified = record.get("qco_notified", False)
    if qco_notified:
        ministry = record.get("qco_issuing_ministry", "Government of India")
        so_num = record.get("qco_gazette_so_number", "")
        eff_date = record.get("qco_effective_date", "")
        products = record.get("qco_products_covered") or []
        products_str = ", ".join(str(p) for p in products) if products else ""

        cert_line = (
            f"Mandatory Quality Control Order (QCO) certification required. "
            f"Gazette notification {so_num} issued by {ministry}"
        )
        if eff_date:
            cert_line += f", effective from {eff_date}"
        cert_line += "."
        parts.append(cert_line)

        scheme = record.get("certification_scheme", "")
        if scheme == "isi_mark":
            parts.append(
                "Certification scheme: BIS ISI Mark (CM/L number) mandatory "
                "for all units manufactured or imported."
            )
        elif scheme == "crs":
            parts.append(
                "Certification scheme: BIS CRS Registration (R-number) mandatory "
                "for each manufacturer and model."
            )

        if products_str:
            parts.append(f"Products requiring certification: {products_str}.")

        mandate_text = str(record.get("qco_mandate_text", "") or "").strip()
        if mandate_text:
            parts.append(f"Mandate: {mandate_text}")
    else:
        parts.append(
            "No mandatory Quality Control Order (QCO) currently notified for this standard. "
            "Certification is voluntary unless specified in tender documents."
        )

    # 6. Status
    status = str(record.get("status", "unknown")).strip()
    if status == "active":
        parts.append("Standard status: Active (current version).")
    elif status == "superseded":
        superseded_by = record.get("superseded_by", "")
        msg = "Standard status: Superseded."
        if superseded_by:
            msg += f" Replaced by {superseded_by}."
        parts.append(msg)
    elif status == "withdrawn":
        parts.append("Standard status: Withdrawn. No longer valid.")
    elif status == "reaffirmed":
        parts.append("Standard status: Reaffirmed. Confirmed valid, no changes needed.")
    elif status == "under_revision":
        parts.append("Standard status: Under Revision. New version forthcoming.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Metadata extraction (what goes in the "metadata" field of the output)
# ---------------------------------------------------------------------------


def extract_metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Extract structured metadata fields for the output record."""
    return {
        "status": record.get("status", "unknown"),
        "year": record.get("year"),
        "latest_version": record.get("latest_version"),
        "source": record.get("data_source", record.get("source", "BIS")),
        "unified_sources": record.get("unified_sources", ["BIS"]),
        "qco_notified": bool(record.get("qco_notified", False)),
        "qco_gazette_so_number": record.get("qco_gazette_so_number"),
        "qco_issuing_ministry": record.get("qco_issuing_ministry"),
        "qco_effective_date": record.get("qco_effective_date"),
        "qco_notification_title": record.get("qco_notification_title"),
        "certification_scheme": record.get("certification_scheme"),
        "is_mandatory": bool(record.get("is_mandatory", False)),
        "products_covered": record.get("qco_products_covered", []),
        "normative_references": record.get("normative_references", []),
        "keywords": record.get("keywords", []),
        "scope_auto_generated": bool(record.get("scope_auto_generated", False)),
        "source_url": record.get("source_url"),
        "qco_source_url": record.get("qco_source_url"),
        "schema_version": record.get("schema_version", "unified_v1"),
    }


# ---------------------------------------------------------------------------
# Fallback embedding (used if sentence-transformers not installed)
# ---------------------------------------------------------------------------


def _fake_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Deterministic pseudo-embedding based on character hashes.
    Used ONLY as a fallback when sentence-transformers is unavailable.
    This allows the pipeline to complete and produce valid JSON structure
    even in environments without ML deps. Krishna can re-run with real embeddings.
    """
    import hashlib
    vec = []
    seed = hashlib.sha256(text.encode()).digest()
    # Use the hash bytes cyclically to fill the vector
    for i in range(dim):
        byte_val = seed[i % len(seed)]
        # Scale to [-1, 1]
        vec.append((byte_val - 128.0) / 128.0)
    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 1e-12:
        vec = [v / norm for v in vec]
    return vec


# ---------------------------------------------------------------------------
# Main export function
# ---------------------------------------------------------------------------


def export(
    merged_records: list[dict[str, Any]],
    output_path: Path,
    use_real_embeddings: bool = True,
) -> dict[str, Any]:
    """
    Generate semantic_text + embeddings for all merged records and write JSON.

    Parameters
    ----------
    merged_records:
        Output of merger.merge().
    output_path:
        Where to write ml_ready_vectors.json.
    use_real_embeddings:
        If True, attempt to use Kshiraj's EmbeddingService.
        If False (or on ImportError), use deterministic fake embeddings.

    Returns
    -------
    Summary statistics dict.
    """
    print(f"\n[MLExporter] Building semantic_text for {len(merged_records)} records...")

    # Build semantic texts
    semantic_texts = [build_semantic_text(r) for r in merged_records]

    # Generate embeddings
    embedding_dim = 384
    embeddings: list[list[float]] = []
    embedding_source = "real"

    if use_real_embeddings:
        try:
            # Add backend root to sys.path so we can import kshiraj
            backend_root = Path(__file__).resolve().parent.parent.parent
            if str(backend_root) not in sys.path:
                sys.path.insert(0, str(backend_root))

            from kshiraj.knowledge.embedding_service import EmbeddingService
            svc = EmbeddingService()
            embedding_dim = svc.dimension
            print(f"[MLExporter] Encoding with EmbeddingService (model={svc.model_name}, dim={embedding_dim})...")
            t0 = time.time()
            embeddings = svc.encode_batch(semantic_texts)
            elapsed = time.time() - t0
            print(f"[MLExporter] Encoded {len(embeddings)} vectors in {elapsed:.2f}s")
            embedding_source = "BAAI/bge-small-en-v1.5"
        except Exception as e:
            print(f"[MLExporter] ⚠ EmbeddingService unavailable ({e})")
            print("[MLExporter] ⚠ Falling back to deterministic pseudo-embeddings.")
            print("[MLExporter]   These are structurally valid but NOT semantically meaningful.")
            print("[MLExporter]   Re-run with sentence-transformers installed for real vectors.")
            embeddings = [_fake_embedding(t, dim=embedding_dim) for t in semantic_texts]
            embedding_source = "pseudo (fallback)"
    else:
        print("[MLExporter] Using pseudo-embeddings (use_real_embeddings=False).")
        embeddings = [_fake_embedding(t, dim=embedding_dim) for t in semantic_texts]
        embedding_source = "pseudo (fallback)"

    # Assemble output records
    output_records: list[dict[str, Any]] = []
    for rec, sem_text, emb in zip(merged_records, semantic_texts, embeddings):
        is_number = str(rec.get("is_number", "")).strip()
        year = rec.get("year")
        record_id = f"{is_number}:{year}" if year else is_number

        output_records.append({
            "id": record_id,
            "is_number": is_number,
            "year": year,
            "title": str(rec.get("title", "")).strip(),
            "scope": rec.get("scope"),
            "semantic_text": sem_text,
            "embedding": emb,
            "embedding_dim": embedding_dim,
            "embedding_model": embedding_source,
            "metadata": extract_metadata(rec),
        })

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_records, f, indent=2, ensure_ascii=False, default=str)

    # Summary stats
    avg_text_len = sum(len(t) for t in semantic_texts) / len(semantic_texts) if semantic_texts else 0
    qco_count = sum(1 for r in output_records if r["metadata"]["qco_notified"])
    mandatory_count = sum(1 for r in output_records if r["metadata"]["is_mandatory"])
    auto_scope_count = sum(1 for r in output_records if r["metadata"]["scope_auto_generated"])

    summary = {
        "output_path": str(output_path),
        "total_records": len(output_records),
        "embedding_dim": embedding_dim,
        "embedding_model": embedding_source,
        "avg_semantic_text_length_chars": round(avg_text_len),
        "qco_notified_count": qco_count,
        "mandatory_certification_count": mandatory_count,
        "auto_generated_scope_count": auto_scope_count,
    }

    print("\n" + "═" * 60)
    print("  ML EXPORT SUMMARY")
    print("═" * 60)
    print(f"  Output:                       {output_path}")
    print(f"  Total records exported:       {summary['total_records']}")
    print(f"  Embedding model:              {embedding_source}")
    print(f"  Embedding dimensions:         {embedding_dim}")
    print(f"  Avg semantic_text length:     {summary['avg_semantic_text_length_chars']} chars")
    print(f"  QCO-notified records:         {qco_count}")
    print(f"  Mandatory certification:      {mandatory_count}")
    print(f"  Auto-generated scopes:        {auto_scope_count}")
    print("═" * 60)
    print("\n  ✓ ml_ready_vectors.json is ready for Krishna's Vector DB upsert.")
    print("    Call: VectorStore.upsert_standards(standards, embeddings)")
    print("═" * 60 + "\n")

    return summary


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ml_ready_vectors.json")
    parser.add_argument(
        "--bis", type=Path, default=_DEFAULT_BIS_INPUT,
        help=f"Path to raw BIS JSON (default: {_DEFAULT_BIS_INPUT})"
    )
    parser.add_argument(
        "--qco", type=Path, default=_DEFAULT_QCO_INPUT,
        help=f"Path to QCO JSON (default: {_DEFAULT_QCO_INPUT})"
    )
    parser.add_argument(
        "--output", type=Path, default=_DEFAULT_OUTPUT,
        help=f"Output path (default: {_DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--no-real-embeddings", action="store_true",
        help="Skip EmbeddingService and use deterministic pseudo-embeddings"
    )
    args = parser.parse_args()

    # Run full pipeline: ingest → merge → export
    from kartikey.data.merger import load_and_merge

    print("=" * 60)
    print("  ETL PIPELINE: Ingestor → Merger → ML Exporter")
    print("=" * 60)

    merged, report = load_and_merge(args.bis, args.qco)
    export(merged, args.output, use_real_embeddings=not args.no_real_embeddings)
