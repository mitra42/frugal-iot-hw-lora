# Frugal-IoT V0.3 (LoRa)

Frugal-IoT V0.2 — a simple, multi-purpose sensor board with onboard charging and an external antenna — plus
an SX1262 LoRa radio, so boards can mesh with each other where there's no WiFi.

**Status:** schematic for review (30 Oct 2026): ESP32-S3-WROOM-1U + Ai-Thinker Ra-01SH, ≈ $17.31 per board for 10,
≈ $11.57 for 100. No layout yet. See `DECISIONS.md` for requirements, decisions and the one open question (power).

Forked from [frugal-iot-hw-sensor](https://github.com/mitra42/frugal-iot-hw-sensor) (V0.2).

## Files

| | |
|---|---|
| `SCHEMATIC.pdf` | schematic, one sheet |
| `BOM.csv` | bill of materials with LCSC (JLCPCB) part numbers; DNP = not fitted |
| `COST-ESTIMATE.txt` | JLCPCB cost for 10 and 100 boards, and the saving without Modbus |
| `DECISIONS.md` | V0.3 requirements, decisions and open questions |
| `datasheets/` | Ai-Thinker Ra-01SH specification (Chinese; pinout, footprint and internal schematic) |
| `v0.2-baseline/` | V0.2 as forked: its README, decision log, schematic, layout, BOM, cost estimate, fabrication and firmware files |
| `frugal_iot_v03/` | KiCad 10 project. The schematic is generated from `claude-tools/schematic/circuit.py`; the .kicad_pcb is still V0.2's until layout |
| `claude-tools/` | scripts Claude uses to regenerate the design — reviewers can ignore |
