"""
database/

SHARED — both Kartikey and Kshiraj use this layer.

Do NOT let either side define competing session factories or ORM bases.

Contents:
  session.py    — SQLAlchemy async session factory
  models/       — ORM table definitions (map to shared.models domain shapes)
  migrations/   — Alembic migration scripts
  init_db.py    — create tables + seed minimal data on startup

Rule:
  Kshiraj owns the repository implementations (standards_store, evidence_store).
  Kartikey owns the session lifecycle and migrations.
  Both agree on the ORM models here.
"""
