# shared/

**Joint ownership — both Kartikey and Kshiraj.**

Agree on everything in this folder before building deeply in your respective areas.
Changes here affect both sides.

## Contents

| Package | Purpose |
|---|---|
| `models/` | Pydantic domain models: `Requirement`, `Standard`, `Evidence`, `Finding`, `Analysis` |
| `contracts/` | Request/response schemas for the API ↔ frontend boundary and backend ↔ AI/ML boundary |
| `utils/` | Shared helpers: logging setup, custom error types, date/time utilities |

## Rule

Do NOT put business logic here.
This package is for data shapes and shared infrastructure only.
