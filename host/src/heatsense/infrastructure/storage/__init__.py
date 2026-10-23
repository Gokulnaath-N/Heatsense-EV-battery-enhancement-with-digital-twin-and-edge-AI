"""Storage Adapters.

Responsibility:
    Implement persistence ports for storing session metadata, telemetry frames, and estimated states in SQLite or files.

Contains:
    SqliteSampleRepository, SqliteSessionRepository, CsvExporter, ParquetExporter.

MAY import:
    stdlib, sqlite3, heatsense.domain, heatsense.application.

MUST NOT import:
    interfaces, firmware.

Goal served: G1, G6
Introduced in: Prompt 01   Implemented in: Prompt 08
"""
