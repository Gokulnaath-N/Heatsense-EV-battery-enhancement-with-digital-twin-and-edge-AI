# Architecture Decision Records (ADRs)

## Purpose
Records significant architectural decisions made on HeatSense, documenting context, alternatives considered, and trade-offs accepted.

## Goal served
G1 (Enforce Architecture by Structure) and G5 (Discoverability). Provides historical rationale for foundational decisions so the team avoids revisiting settled choices without new evidence.

## Contains
ADR template and decision records:
- `0000-template.md`: Standard template for proposing and documenting an ADR.
- `0001-repository-layout.md`: Decision record for the monorepo structure, sibling safety boundaries, and hexagonal host layout.

## How to Propose an ADR
1. Copy `0000-template.md` to a new sequential file: `NNNN-short-descriptive-title.md`.
2. Populate Context, Decision, Alternatives Considered (with explicit rejection rationale), and Consequences (both positive and negative).
3. Set status to `PROPOSED` and submit in a phase branch for human review.
4. Once accepted, change status to `ACCEPTED` and update this index.

## Index
| Number | Title | Status | Date |
| :--- | :--- | :--- | :--- |
| [0001](0001-repository-layout.md) | Monorepo layout with sibling safety boundaries and hexagonal host | ACCEPTED | 2026-10-24 |

## Rules
- MAY: Propose architectural revisions, new port definitions, or communication protocol changes.
- MUST NOT: Revoke locked decisions (safety boundary, vocabulary, one-cell scope) without explicit human owner approval.

## Status
Active.

## Owner
Software / Human decision

## Related documents
- [0000-template.md](0000-template.md)
- [0001-repository-layout.md](0001-repository-layout.md)
