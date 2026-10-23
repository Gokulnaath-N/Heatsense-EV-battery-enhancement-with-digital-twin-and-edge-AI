# protocol

## Purpose
Documents the binary serial telemetry protocol and framing specification connecting the ESP32 firmware and the Python host.

## Goal served
G2 (Make the Safety Boundary Visible) and G3 (Contract First). Defines byte layouts, CRC-16-CCITT polynomials, framing delimiters, and unit conversions in one authoritative location.

## Contains
Planned protocol specifications and framing guides:
- Framing format: magic sync bytes, payload length, sequence counter, payload, and CRC-16.
- Packet types: periodic telemetry frame, device status frame, host command frames (ARM, DISARM, PING).
- Wire unit specifications: millivolts (`v_mv`), milliamps (`i_ma`), deci-Celsius (`t_dc`).

## Rules
- MAY: Specify byte offsets, struct packing, endianness (little-endian), and error detection polynomials.
- MUST NOT: Allow divergent protocol definitions between firmware and host; all golden vectors must validate across both decoders.

## Status
Planned in Prompt 04.

## Owner
Software

## Related documents
- [contracts/README.md](../../contracts/README.md)
- [docs/glossary.md](../glossary.md)
