# Contributing to HeatSense

All contributors and AI agents must follow this disciplined workflow to maintain system safety boundaries, architectural cleanliness, and reproducibility.

---

## Branch Naming Conventions

All development occurs on focused phase branches branched from `main`:

`phase/<nn>-<slug>`

Examples:
- `phase/01-structure`
- `phase/02-toolchain`
- `phase/05-domain`
- `phase/06-simulator`

Bug fixes on existing phases use:
`fix/<issue-number>-<slug>`

---

## Commit Message Standards

HeatSense strictly adheres to the [Conventional Commits](https://www.conventionalcommits.org/) specification:

`<type>: <description>`

Allowed types:
- `feat`: A new feature or capability introduced into a layer.
- `fix`: A bug fix or correction to an algorithm or adapter.
- `docs`: Documentation updates, ADRs, or glossary entries.
- `chore`: Repository maintenance, skeleton setup, or tooling configuration.
- `test`: Adding or refactoring unit, contract, integration, or property tests.
- `refactor`: Internal code adjustments that alter neither behavior nor interfaces.

Rules:
- Keep the subject line concise (under 72 characters), written in the imperative mood.
- Group changes into small, atomic, logical commits.

---

## Definition of Done (DoD)

A task or phase is considered complete only when all of the following criteria are verified:

1. **Plan Reviewed**: A formal PLAN artifact was documented and approved prior to writing code.
2. **Tests Added**: Unit tests (and contract/property tests where appropriate) cover all new code. Domain coverage must meet or exceed 90 %.
3. **Quality Gate Green**: The automated verification script (`python scripts/verify_structure.py` for Prompt 01; `scripts/check.sh` / `scripts/check.ps1` from Prompt 02 onward) passes completely.
4. **Documentation Synchronized**: All relevant READMEs, ADRs, and API schemas are updated.
5. **No Forbidden Wording**: Zero occurrences of prohibited claims or terminology (see [docs/claims-policy.md](docs/claims-policy.md)).
6. **Walkthrough Documented**: A WALKTHROUGH artifact containing real terminal command outputs and a checklist against criteria is produced.

---

## Proposing Architecture Changes

Architectural modifications (such as altering port interfaces, introducing a new layer, or modifying communication protocols) require an Architecture Decision Record (ADR):

1. Consult [docs/adr/README.md](docs/adr/README.md) and copy [docs/adr/0000-template.md](docs/adr/0000-template.md).
2. Clearly formulate the context, proposed decision, alternatives considered (with rejection reasons), and positive/negative trade-offs.
3. Submit the ADR in a phase branch for human review and approval.
4. Locked decisions (safety boundary, vocabulary, one-cell scope) cannot be reversed without explicit authorization from the project owner.

---

## Gate Tags

Formal phase transitions are marked in git using annotated release gate tags:

`gate-<nn>-<slug>`

Examples:
- `gate-01-structure`
- `gate-02-toolchain`
- `gate-06-simulator`

Rules for Gate Tags:
- A gate tag is created only after all acceptance criteria for that phase are met and confirmed by a human reviewer.
- Never push an unverified or failing commit to a gate tag.
