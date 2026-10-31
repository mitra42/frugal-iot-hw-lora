# Frugal-IoT V0.3 (LoRa) — requirements and decision log

Status: **laid out and routed, for review (31 Oct 2026)** — 84 × 37 mm, DRC clean (0 unconnected, schematic parity 0);
`SCHEMATIC.pdf`, `PCB-LAYOUT.pdf`, `BOM.csv`, `COST-ESTIMATE.txt`, JLCPCB files in `fabrication/`; one open question (Q3, power). The KiCad project (`frugal_iot_v03/`, renamed from
V0.2's) and `claude-tools/` started as V0.2's; V0.2's own files and decision log are in
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

## Decided (30 Oct 2026, Mitra's answers to Q1–Q6)

**L1 — Module: ESP32-S3-WROOM-1U-N4** (C2980296, $4.06 @10 / $3.42 @100, 2,000 in stock) (Mitra, Q1). Why:
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

**L2 — Radio: Ai-Thinker Ra-01SH** (C2764087, $3.95 @10 / $2.96 @100, 240 in stock) (Mitra, Q2). SX1262, 803–930 MHz
(covers R5), U.FL on the module, 22 dBm. It drives its own antenna switch from the SX1262's DIO2, so it needs
only the 7 pins above. Plain crystal, no TCXO: frequency drifts a little with temperature, which matters
most at high spreading factors and narrow bandwidths (Frugal-IoT uses SF7 / 125 kHz today, so it's fine).
- Alternative: Ebyte E22-900M22S (C411293, $6.28 / $5.12, 185 in stock): TCXO (more stable outdoors),
  stamp holes + U.FL, but 2 more pins for TXEN/RXEN and ~$2.30 more per board.
- Not proposed for a first spin: the bare SX1262 (C191341, $1.89 @100) — needs our own matching network, RF
  switch and crystal/TCXO, RF layout, and has no module certification.
- Stock of both modules is thin: fine for 10 boards; pre-order through JLCPCB for 100s.

**L3 — S3 pin map** (radio on the same GPIOs as the Heltec V3/V4, so their firmware setup carries over;
analog inputs on ADC1, which works while WiFi is on; strapping pins 0, 3, 45, 46 avoided). As revised for the
layout in L19:

| GPIO | use |
|---|---|
| 0 | BOOT button |
| 1, 2 | Spares (ADC1) → J13 pins 6, 9 |
| 4, 5 | Sensor 1, sensor 2 (ADC1) → J2 pins 6, 9 |
| 6 | Battery sense (ADC1) |
| 8, 9, 10, 11 | LoRa NSS, SCK, MOSI, MISO |
| 12, 13, 14 | LoRa RESET, BUSY, DIO1 |
| 15 | nRAIL_EN (3V3_SW, active low) |
| 17, 18 | I2C SDA, SCL → J2 pins 2, 3 |
| 19, 20 | USB D−/D+ |
| 21 | Status LED (active low) |
| 38 | RS485 DE/RE |
| 43, 44 | UART0 TX/RX → RS485 or J3 pins 2–3 |
| 36, 39, 41, 42, 47, 48 | Spare → J5 holes (L10) |
| 3, 7, 16, 35, 37, 40, 45, 46 | Not connected |

**L4 — Radio powered from an always-on supply, not 3V3_SW** (its own regulator since L18): the SX1262 sleeps at under 2 µA, and the mesh
needs it to wake on its own schedule. Its 120 mA transmit peak is within the ME6211's 500 mA. Local
decoupling at the module; RESET pulled up so the radio stays out of reset while the ESP32 sleeps.

**L5 — Two U.FL antennas at opposite ends of the board** (WiFi on the ESP32 module, LoRa on the Ra-01SH) to
keep them apart; no RF tracks on our board.

**L6 — Firmware: board variant plus build flags, no library change expected.** `loramesher.cpp` already
accepts any board that defines `LORA_CS`, `LORA_RST`, `LORA_IRQ`, `LORA_IO1`, `LORA_MOSI`, `LORA_MISO` and
`LORA_RADIO_TYPE`; a `pins_arduino.h` variant (as V0.2's) plus `-D SYSTEM_LORAMESHER_WANT` and
`-D LORA_RADIO_TYPE=loramesher::RadioType::kSx1262` in a new PlatformIO env should be enough. To check: the Heltec
entry maps `LORA_IRQ`/`LORA_IO1` the opposite way to the SX1262's DIO1/BUSY names ("bizarre swap" comment) —
confirm which LoRaMesher expects before fixing the variant.
Checked against LoRaMesher main (6ffb8fc, 23 Sep 2026) and RadioLib 7.8.1 (30 Oct 2026): their defaults suit the
Ra-01SH as they are — SX1262 DC-DC regulator (hard-coded; the Ra-01SH has the 15 µH inductor for it), no TCXO
(default 0.0 V; the Ra-01SH has a crystal — do **not** copy the Heltec `LORA_TCXO_VOLTAGE 1.8F`), and DIO2 as RF
switch (RadioLib `begin()` sets it). LoRaMesher sleeps the radio with an SPI sleep command in its TDMA sleep
slots and light-sleeps the ESP32; it never powers the radio off, so no radio power control is needed.

**L7 — Board grows to about 80 × 37 mm** (from 64 × 37) for the radio module (~17 × 16 mm) and the larger
ESP32 module. To be confirmed at placement.

**L8 — Cost:** about +$5.60 per board @10 and +$4.20 @100 over V0.2 (module +$1.22 / +$1.18, radio +$3.95 /
+$2.96, one more feeder fee, slightly larger board), i.e. ≈ $17 / $11.40. Plus a second antenna per board,
bought separately. Leaving Modbus off still saves about $1. A proper estimate follows the schematic.

**L9 — Modbus (RS485) fitted by default**, as V0.2 D29 (Mitra, Q4). Board uses: 4 sensor inputs (J2 S1/S2,
J13 GPIO4/GPIO5), I2C, and Modbus — or 2 more GPIOs / UART on J3 pins 2–3 with the solder jumpers re-bridged.

**L10 — Spare GPIOs (7, 38–42, 47, 48) go to a row of unfitted 2.54 mm holes mid-board, with GND and 3V3_SW**
(Mitra, Q5): no connector fitted and no cost beyond board area; a header can be soldered in later if ever
needed. Extra devices such as an OLED would go on I2C, not these pins. Pin names on the back silkscreen
as V0.2 D33.

**L11 — The same board is used as a LoRa-to-WiFi gateway** (Mitra, Q6: at least one node in each mesh).
No hardware difference — the gateway role is firmware. A gateway keeps WiFi and LoRa on together
(tens of mA continuously), so in practice it runs from USB or a larger solar
panel and cell rather than a small cell; this feeds into Q3.

## Schematic (30 Oct 2026)

**L12 — Ra-01SH wiring, from Ai-Thinker's Ra-01SH specification V1.1** (`datasheets/`). The module has a 32 MHz
crystal (no TCXO, so DIO3 unused), an IPEX socket, and its own RF switch driven from DIO2 — inside the module
TXEN is joined to DIO2 and RXEN is not connected. So pads 1 (ANT), 5 (TXEN), 7 (DIO2), 8 (DIO3) and 11 (RXEN)
are left open; only the 7 SPI/control lines go to the S3. C14 10 µF + C15 100 nF at its 3V3 pin. Firmware defaults
already set DIO2 as the RF switch (L6).

**L13 — R22 pulls LORA_NSS and R23 pulls LORA_RST up to +3V3_RF (10k)**, as the Heltec V3 does, so the radio stays deselected and out of
reset while the ESP32 boots or deep-sleeps and its pins float.

**L14 — Ra-01SH footprint is project-made** (`frugal_iot_v03/frugal.pretty/Ai-Thinker-Ra-01SH`, generated by
`buildlib.py`): KiCad's Ra-01 footprint has the same pinout but its pads stop 0.27 mm short of the Ra-01SH's
inner pad ends, and Ai-Thinker says PCB pads may extend outward but not inward. 2 × 8 pads, 2.0 mm pitch,
2.0 × 1.0 mm, from 6.75 mm to 8.75 mm either side of centre. Pin 1 top-left, as the Ra-01.

**L15 — S3 straps:** GPIO0 = BOOT (R12 pull-up + SW2). GPIO3, 45 and 46 are left unconnected so their internal
defaults apply (3.3 V flash, normal boot). V0.2's strap pull-ups on GPIO2 and GPIO8 are gone (C3-only), so the
status LED (GPIO21) needs no pull-up. GPIO35–37 left unconnected.

**L16 — Net and reference changes from V0.2:** RS485 DE/RE is GPIO38 (net `RS485_DE`, was `GPIO10`); J13 carries
GPIO1/GPIO2 (L19); J5 is now the 10-hole spare row (L10) instead of V0.2's 3-pad GPIO10 position.
Resistors after R12 renumbered (two strap resistors removed): LED R13; I2C pull-ups R14/R15; sensor options
R16/R17; RS485 R18–R21; LoRa pull-ups R22/R23. New: U6 (radio), C14/C15; U7 + C16 (radio regulator, L18).

**L17 — Cost from the schematic** (`COST-ESTIMATE.txt`, prices 31 Oct 2026): ≈ $17.31 per board for 10,
≈ $11.58 for 100 (with L18; test points cost nothing), bare PCB still a placeholder — as estimated in L8. Antennas extra.

**L18 — Two RT9080-33GJ5 regulators replace the ME6211** (C841192, Richtek, TSOT-23-5; Mitra agreed 30 Oct): U3
for the ESP32, sensors and RS485 (+3V3), U7 for the radio alone (+3V3_RF). Compared with reference designs:
the Heltec WiFi LoRa 32 V3.2 feeds radio and ESP32 from one LDO; the LilyGo T3-S3 V1.3 gives the radio its own
RT9080 (enable on by default, an unfitted resistor for GPIO control).
- Why the RT9080: 2 µA quiescent (ME6211: 60 µA), 600 mA (ME6211: 500 mA), and about half the ME6211's dropout
  at the same current. Same pins as the ME6211 (1 VIN, 2 GND, 3 EN, 4 NC, 5 VOUT; Richtek DS9080-09). Same
  part twice = one feeder fee. Two cost about +22¢ per board @10, +15¢ @100 over one ME6211; sleep current
  4 µA for both instead of 60 µA.
- Why a separate radio regulator: keeps the S3's WiFi transmit bursts (to ~350 mA) and the radio's transmit
  (~120 mA) off one 500 mA LDO, and keeps WiFi load steps off the radio's supply. A margin improvement, not a
  must — Heltec's shared rail works.
- EN tied to VIN on both: always on. No GPIO control (Mitra): the SX1262 sleeps under 1 µA on command and
  LoRaMesher never powers it off (L6).
- Dropout (Mitra's concern): 0.31 V typical / 0.53 V max at the full 600 mA — about 0.5 Ω, so ~0.18 V at a
  350 mA WiFi peak and ~0.06 V at a 120 mA LoRa transmit. Below 3.3 V + dropout the LDO doesn't cut out: its
  output follows the cell minus that drop. The ESP32-S3 runs down to 3.0 V and the Ra-01SH to 2.7 V, so the
  board keeps working until the cell is roughly 3.2–3.3 V under load, by which point a LiPo has only a few
  percent left. A buck-boost converter would reach the last few percent but costs more and idles at tens of µA.
- Not changed in V0.2 or the irrigation board, which still use the ME6211; the same swap would save ~58 µA there.

## Layout (31 Oct 2026)

**L19 — Placement and pin-map changes made for routing** (Mitra agreed 31 Oct; first attempt at 84 mm left 20+
connections the router couldn't make, so these were found by trial):
- ESP32 module top-left, U.FL at its top end; Ra-01SH below-right of it, rotated 180° so its SPI pads face the
  module's LoRa pins. Its IPEX ends up near the middle of the bottom edge, ~30 mm from the ESP32's U.FL rather
  than at opposite ends (L5): fine with cables to panel-mounted antennas.
- GPIOs moved so each signal leaves the module on the side facing where it goes (the LoRa pins are unchanged):
  sensors 1/2 = GPIO4/5 (left side, towards J2), J13 spares = GPIO1/2 (right side, towards J3/J13), RS485 DE =
  GPIO38, J5 spares = 36, 37, 39–42, 47, 48 (GPIO36/37 are free on the N4 module, which has no octal PSRAM).
  GPIO7 and GPIO16 are now unused.
- J5 is a 2 × 5 block of holes (2.54 mm) on the bottom edge rather than a 1 × 10 row.
- J4 (cell) moved to the bottom edge beside the charger; J6 (5 V in) beside the USB-C, which carries the same net.
- A 0.35 mm no-track strip along every board edge (rule areas), so the router can't hug the outline.
- J6 (5 V in) moved beside the USB-C (same net); J5 moved to the top edge beside the module's spare-GPIO pins.
- Result: 84 × 37 mm (Mitra: as short as possible; a first try at 92 mm routed more easily). DRC: 0 unconnected,
  schematic parity 0; the 48 notes left are the accepted ones from V0.2 (butting terminal blocks, connector
  silkscreen at the board edge, the module footprint's widened thermal-via drills).
- J5 holes 4 and 6 are unconnected: GPIO37 and GPIO40 could not be routed to them at 84 mm, so J5 carries six
  spare GPIOs (36, 39, 41, 42, 47, 48) with GND and 3V3_SW. Labelled "NC" on the back.
- Routing: Freerouting 2.1.0, each run's result fed back in as the start of the next (`route/merge.py`,
  `route/loop.sh`), then the last three connections by a small grid router (`route/astar.py`) and a clean-up
  (`patch_v03.py`, `prune.py`). LORA_MOSI has one via under the module (tented, clear of its pads).

**L20 — Test points on every supply rail** (Mitra, 31 Oct): TP1–TP7 on VBUS, VBAT, VSYS, +3V3, +3V3_SW, +3V3_RF
and GND. Bare 1.5 mm SMD pads on the top copper (KiCad TestPoint_Pad_D1.5mm): no part, no cost, not in the BOM or
pick-and-place file. Each is labelled on the silkscreen with its rail name instead of its reference; they sit
together in the power area between the module and the charger. A probe tip or a grabber hook lands on them; a wire can be
soldered on.

## Open questions

**Q3 — Power budget with LoRa (decide later, Mitra).** If a node routes for others, the radio and ESP32 spend
much more time awake than a WiFi sensor in deep sleep. LoRaMesher now has a duty-cycle / minimum-sleep setting
(Frugal-IoT sets `LORA_DUTY_CYCLE` 1.0 today, i.e. always on). How long a node must run on a cell, whether
some nodes are leaf-only and can sleep, and how gateways (L11) are powered decide the cell and solar sizing —
and whether the charger should default to 500 mA (V0.2 D8). Doesn't block the schematic: the charge-current
jumper already covers both.

Settled 30 Oct 2026: Q1 → L1 (S3), Q2 → L2 (Ra-01SH), Q4 → L9 (Modbus fitted), Q5 → L10 (unfitted holes),
Q6 → L11 (gateway is the same board).
