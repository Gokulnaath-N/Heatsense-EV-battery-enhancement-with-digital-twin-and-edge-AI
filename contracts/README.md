# contracts

## Purpose
Acts as the single source of truth for the binary and structured contracts shared between firmware, host, and dashboard, preventing cross-language divergence.

## Goal served
G2 (Make the Safety Boundary Visible) and G3 (Contract First). Guarantees that neither firmware nor host duplicates protocol definitions independently.

## Contains
Language-agnostic specifications, binary test fixtures, and machine-generated schemas:
- `golden/`: Canonical serialized binary telemetry frames and command packets verified against both C++ and Python decoders.
- `schemas/`: Machine-readable JSON Schemas generated from API DTOs for client validation.

## Rules
- MAY: Contain binary test vectors, protocol specifications, and schema definitions.
- MUST NOT: Contain executable Python or C++ application code.

## Status
Active; golden frames and complete schemas introduced in Prompt 04.

## Owner
Software

## Related documents
- [docs/protocol/README.md](../docs/protocol/README.md)
- [docs/adr/0001-repository-layout.md](../docs/adr/0001-repository-layout.md)
