# Frugal-IoT V0.3 (LoRa) — requirements and decision log

Status: **requirements, for review (30 Oct 2026)** — nothing drawn yet. The KiCad project (`frugal_iot_v02/`) and
`claude-tools/` are V0.2's, copied as the starting point; V0.2's own files and decision log are in
`v0.2-baseline/`. Decisions are numbered L1, L2… so they can't be confused with V0.2's D-numbers. Everything
in V0.2 (`v0.2-baseline/DECISIONS-V0.2.md`) carries over unless a decision here changes it.

Prices and stock are from JLCPCB's parts API on 30 Oct 2026 (Extended parts: $3.07 feeder fee per order).

## Requirements

**R1 — V0.2 plus an SX1262 LoRa radio.** Same purpose, same PCBA route (JLCPCB, Economic, top side), same
power design (USB-C, TP4056, XB5353A, ME6211, switched 3V3_SW sensor rail), same connector scheme
(J2/J12 sensors, J3/J13 serial + spares, J4 cell, J6 5 V in), same silkscreen labelling on both sides.

**R2 — Cost still matters**: cheapest module that does the job, but not at the cost of losing V0.2 features.
Mitra is flexible on how many sensor pins remain.

**R3 — External antennas only** (U.FL): one for WiFi, one for LoRa.

**R4 — Works with Frugal-IoT's existing LoRa stack** (LoRaMesher over RadioLib), ideally without library changes.

**R5 — One board for every region Frugal-IoT is used in**: AU915 (Australia), AS923 (Indonesia), IN865
(India), EU868 (Kenya). The band is chosen in firmware (`SYSTEM_LORAMESHER_FREQUENCY`).

**R6 — Height stays 37 mm** (fits a 40 mm pipe); length grows as needed.

## Proposed (for Mitra to confirm)

**L1 — Module: ESP32-S3-WROOM-1U-N4** (C2980296, $4.06 @10 / $3.42 @100, 2,000 in stock). Why:
- The C3 has no free pins: the radio needs 7 (SCK, MOSI, MISO, NSS, RESET, BUSY, DIO1) and V0.2 uses all 15
  of the C3's. Freeing 7 would mean dropping Modbus, both spares and the LED, and using the BOOT pin.
- ESP32-C6-MINI-1U-H4 (C20627095, $3.79 / $3.30, 2,200 in stock) has exactly the 7 extra pins and is 12¢
  cheaper at 100, but: LoRaMesher hasn't been run on a RISC-V ESP32 in Frugal-IoT yet, the module has ground
  pads underneath (JLCPCB may charge X-ray), and it leaves no spare pins. The C6-WROOM-1U is out of stock.
- The S3 + SX1262 pairing is the Heltec WiFi LoRa 32 V3/V4, which Frugal-IoT already supports, so the
  firmware path is proven. ~36 GPIOs leave spares. Castellated edge pads like the C3 module.
- Costs: module +$1.22 per board @10, +$1.18 @100 over the C3. Bigger (19.2 × 18 mm vs 18 × 14.3 mm).
  Deep-sleep current is similar (single-digit µA); active current is higher than the C3.
- S2 modules are out of stock and have no Bluetooth.

**L2 — Radio: Ai-Thinker Ra-01SH** (C2764087, $3.95 @10 / $2.96 @100, 240 in stock). SX1262, 803–930 MHz
(covers R5), U.FL on the module, 22 dBm. It drives its own antenna switch from the SX1262's DIO2, so it needs
only the 7 pins above. Plain crystal, no TCXO: frequency drifts a little with temperature, which matters
most at high spreading factors and narrow bandwidths (Frugal-IoT uses SF7 / 125 kHz today, so it's fine).
- Alternative: Ebyte E22-900M22S (C411293, $6.28 / $5.12, 185 in stock): TCXO (more stable outdoors),
  stamp holes + U.FL, but 2 more pins for TXEN/RXEN and ~$2.30 more per board.
- Not proposed for a first spin: the bare SX1262 (C191341, $1.89 @100) — needs our own matching network, RF
  switch and crystal/TCXO, RF layout, and has no module certification.
- Stock of both modules is thin: fine for 10 boards; pre-order through JLCPCB for 100s.

**L3 — Proposed S3 pin map** (radio on the same GPIOs as the Heltec V3/V4, so their firmware setup carries over;
analog inputs on ADC1, which works while WiFi is on; strapping pins 0, 3, 45, 46 avoided):

| GPIO | use |
|---|---|
| 0 | BOOT button |
| 1, 2 | Sensor 1, sensor 2 (ADC1) → J2 pins 6, 9 |
| 4, 5 | Spares (ADC1) → J13 pins 6, 9 |
| 6 | Battery sense (ADC1) |
| 7 | Spare (ADC1) → J5 pad (was GPIO10) |
| 8, 9, 10, 11 | LoRa NSS, SCK, MOSI, MISO |
| 12, 13, 14 | LoRa RESET, BUSY, DIO1 |
| 15 | nRAIL_EN (3V3_SW, active low) |
| 16 | RS485 DE/RE |
| 17, 18 | I2C SDA, SCL → J2 pins 2, 3 |
| 19, 20 | USB D−/D+ |
| 21 | Status LED (active low) |
| 43, 44 | UART0 TX/RX → RS485 or J3 pins 2–3 |
| 38–42, 47, 48 | Free — candidates for a further connector (L8) |

**L4 — Radio powered from the always-on 3V3, not 3V3_SW**: the SX1262 sleeps at under 2 µA, and the mesh
needs it to wake on its own schedule. Its 120 mA transmit peak is within the ME6211's 500 mA. Local
decoupling at the module; RESET pulled up so the radio stays out of reset while the ESP32 sleeps.

**L5 — Two U.FL antennas at opposite ends of the board** (WiFi on the ESP32 module, LoRa on the Ra-01SH) to
keep them apart; no RF tracks on our board.

**L6 — Firmware: board variant plus build flags, no library change expected.** `loramesher.cpp` already
accepts any board that defines `LORA_CS`, `LORA_RST`, `LORA_IRQ`, `LORA_IO1`, `LORA_MOSI`, `LORA_MISO` and
`LORA_RADIO_TYPE`; a `pins_arduino.h` variant (as V0.2's) plus `-D SYSTEM_LORAMESHER_WANT` and
`-D LORA_RADIO_TYPE=loramesher::RadioType::kSx1262` in a new PlatformIO env should be enough. No
`LORA_TCXO_VOLTAGE` for the Ra-01SH (crystal); 1.8 V for the E22. To check: the Heltec entry maps
`LORA_IRQ`/`LORA_IO1` the opposite way to the SX1262's DIO1/BUSY names ("bizarre swap" comment) — confirm
which LoRaMesher expects before fixing the variant.

**L7 — Board grows to about 80 × 37 mm** (from 64 × 37) for the radio module (~17 × 16 mm) and the larger
ESP32 module. To be confirmed at placement.

**L8 — Cost:** about +$5.60 per board @10 and +$4.20 @100 over V0.2 (module +$1.22 / +$1.18, radio +$3.95 /
+$2.96, one more feeder fee, slightly larger board), i.e. ≈ $17 / $11.40. Plus a second antenna per board,
bought separately. Leaving Modbus off still saves about $1. A proper estimate follows the schematic.

## Open questions

**Q1 — S3 or C6?** (L1). S3 proposed; C6 if the 12¢ matters more than firmware risk and spare pins.

**Q2 — Ra-01SH or E22-900M22S?** (L2). Ra-01SH proposed on cost.

**Q3 — Power budget with LoRa.** If a node routes for others, the radio and ESP32 spend much more time awake
than a WiFi sensor in deep sleep. LoRaMesher now has a duty-cycle / minimum-sleep setting (Frugal-IoT sets
`LORA_DUTY_CYCLE` 1.0 today, i.e. always on). How long a node must run on a cell, and whether some nodes are
leaf-only and can sleep, decides the cell and solar sizing — and whether the charger should default to
500 mA (D8).

**Q4 — Modbus fitted by default?** (V0.2 D29: yes.)

**Q5 — Use the free S3 pins?** (L3) e.g. a third 5-way block, or leave as unfitted pads.

**Q6 — Gateway role.** Does any node need to be a LoRa-to-WiFi gateway (needs WiFi and LoRa awake together)?
Same hardware either way; it only affects power (Q3).
