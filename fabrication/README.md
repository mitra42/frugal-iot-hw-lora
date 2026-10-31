# Frugal-IoT V0.3 LoRa — JLCPCB order files (31 Oct 2026)

Board: 84 × 37 mm, 2 layers, 1.6 mm FR-4, 1 oz copper, 4 × M2 holes. Min track 0.25 mm, min clearance 0.15 mm
(USB pair) / 0.2 mm elsewhere, min drill 0.3 mm, no copper within 0.35 mm of the edge — all JLCPCB standard.

| File | Upload where |
|---|---|
| `gerbers.zip` | PCB order — "Add gerber file" |
| `BOM_JLCPCB.csv` | PCB Assembly — BOM (Comment, Designator, Footprint, LCSC Part #) |
| `CPL_JLCPCB.csv` | PCB Assembly — CPL / pick-and-place (Designator, Mid X, Mid Y, Layer, Rotation) |

60 placed parts, 27 part numbers, RS485, J4 (cell) and J6 (5 V in) included. Not fitted (excluded from both
files): J5 (spare-GPIO holes), J7 (external LED), R17, C11, the solder jumpers and the test-point pads TP1–TP7.

**Before paying, check JLCPCB's assembly preview** (the pink dot marks pin 1). The CPL carries V0.2's
corrections for JLCPCB's models (SOT-23, SOIC-8, U2 XB5353A, the connectors). The new parts — U4 (ESP32-S3
module), U6 (Ra-01SH) and U3/U7 (RT9080, TSOT-23-5) — have not been through the preview yet, so check them
first. Expected pin 1 (or cathode):

| Part | Pin 1 / cathode |
|---|---|
| U4 ESP32-S3 module, U5 | top-left |
| U1 | bottom-right |
| U2 | top-right |
| U3, U7 (RT9080) | bottom-right |
| U6 Ra-01SH | bottom-right (its IPEX socket is at that corner) |
| Q1, Q2 | top-left |
| D5 | top-right |
| D3 (SS34) | band on the right |
| LEDs | D1 cathode at the top; D2 and D4 at the bottom |

Every terminal-block screw and J4/J6 should sit over its own pads. Tick "Confirm parts placement" (~$0.45) as well.

Assembly: Economic, top side only. J2 + J12 and J3 + J13 (pairs of XY308-2.54-5P that butt together as 10-way
blocks), J4 and J6 are through-hole and hand-soldered by JLCPCB — or untick them and solder yourself.

Without Modbus (saves ≈ $1.30 per board at 10): set U5, C13, R18–R21, D5 and J3 to DNP in
`claude-tools/schematic/circuit.py` and regenerate the files (V0.2 decision D29).

Regenerate: `claude-tools/layout/fab.sh` on the Mac (DRC + Gerbers + drill + placement + BOM), then
`python3 claude-tools/layout/jlc_files.py`.
