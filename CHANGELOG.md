# Changelog

All notable changes to the HeatSense project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Repository directory skeleton across firmware, host, dashboard, contracts, data, runs, and docs.
- Strict architecture boundaries enforcing Clean / Hexagonal layout for the host.
- Hardware safety boundary isolating firmware relay control from host advisory layers.
- Governance policies: `AGENTS.md`, `CONTRIBUTING.md`, `docs/glossary.md`, `docs/claims-policy.md`, and `docs/safety-limits.md`.
- Architecture Decision Record `docs/adr/0001-repository-layout.md`.
- Automated standard library verification tool `scripts/verify_structure.py`.
- Version control configurations `.gitignore`, `.gitattributes`, and `.editorconfig`.
