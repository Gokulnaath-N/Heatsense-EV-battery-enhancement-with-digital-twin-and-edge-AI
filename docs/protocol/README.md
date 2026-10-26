# protocol

## Purpose
Documents the serial wire telemetry protocol, frame grammar, and interface contract connecting the ESP32 firmware and the Python host.

## Goal served
G1 (Unambiguous Interfaces) and G2 (Make the Safety Boundary Visible). Defines byte layouts, CRC-16-CCITT algorithms, framing delimiters, and command semantics in one authoritative specification.

## Contains
- [telemetry-v1.md](telemetry-v1.md): The byte-exact specification of HeatSense Telemetry Protocol v1.

## Rules
- MAY: Specify byte offsets, framing grammars, integer ranges, and error detection polynomials.
- MUST NOT: Allow divergent protocol definitions between firmware and host; all golden vectors must validate across both decoders.

## Status
Draft for review.

## Owner
Systems & Protocol Engineer

## Related documents
- [contracts/golden/README.md](../../contracts/golden/README.md)
- [docs/glossary.md](../glossary.md)
- [docs/adr/0003-telemetry-transport-ascii-crc16.md](../adr/0003-telemetry-transport-ascii-crc16.md)
- [docs/adr/0004-host-device-command-subset.md](../adr/0004-host-device-command-subset.md)
