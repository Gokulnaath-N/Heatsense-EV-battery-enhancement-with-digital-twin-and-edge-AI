# hardware

## Purpose
Maintains hardware assembly documentation, electrical schematics, pinout tables, sensor calibration logs, and bench verification test records.

## Goal served
G4 (Hardware Independence) and G6 (Reproducibility and Hygiene). Decouples physical hardware specifications and test logs from the software repository while providing an authoritative record for hardware integration.

## Contains
Hardware design documentation and verification records:
- Schematic diagrams and pin allocation tables for ESP32-WROOM-32, INA219, DS18B20 trio, and 5V relay module.
- Bill of Materials (BOM) including 18650 cell holder, 10 ohm / 10 W load resistor, and test leads.
- Hardware bench testing procedures and physical validation checklists.

## Rules
- MAY: Detail physical wiring, noise decoupling capacitors, power rail requirements, and bench measurements.
- MUST NOT: Require hardware presence to execute software unit, contract, or simulation test suites.

## Status
Planned (Maintained in coordination with hardware teammate).

## Owner
Hardware teammate

## Related documents
- [docs/safety-limits.md](../safety-limits.md)
- [firmware/README.md](../../firmware/README.md)
