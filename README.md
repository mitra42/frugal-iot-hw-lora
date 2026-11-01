# Frugal-IoT V0.3 LoRa

A simple, un-opinionated, multi-purpose sensor board, that can be wired to sensors using most common interfaces (I2C, ModBus, OneWire, Analog) with onboard charging and external antennas, plus a LoRa radio so boards can talk to each other where there is no WiFi.

This is the [Frugal-IoT V0.2 sensor board](https://github.com/mitra42/frugal-iot-hw-sensor) with an SX1262 LoRa radio added.

**Status:** laid out and routed, for review (31 Oct 2026): 84 × 37 mm, DRC clean, JLCPCB files ready but not ordered. About USD17.31 per board for 10 and USD11.58 for 100. See `DECISIONS.md` for requirements, decisions and the one open question (power budget with LoRa).

## Hardware Features

* ESP32-S3-WROOM-1U
* Ai-Thinker Ra-01SH LoRa radio (SX1262, 803–930 MHz), so one board covers AU915, AS923, IN865 and EU868 — the band is set in firmware.
* Two U.FL sockets for external antennas, one for WiFi (on the ESP32 module) and one for LoRa (on the radio module) — see [Antennas](#antennas).
* LoRa radio on its own always-on regulator, isolated from WiFi load and sleeping at under 1µA.
* USB-C for power and programming (e.g. using a $10 security camera solar panel)
* Protected charger circuitry for a single LiPo cell (~250mA), will work with really small cells (e.g. salvaged from vapes) or by adding a solder bridge can charge an 18650 cell at ~500mA
* Low-quiescent regulators (2µA each), so the board draws very little while asleep.
* Sensors controlled by a switched 3.3V sensor rail, allowing much lower power consumption in sleep.
* I2C support on J2
* Two sensor inputs on J2 (pins 6 & 9, GPIO4 & GPIO5) can be used for analog, OneWire etc, pads to add pull up resistor or smoothing capacitor if required.
* Two extra sensors on J3 (pins 6 & 9, GPIO1 & GPIO2)
* RS485(Modbus) on J3 pins 2 & 3, (can be omitted to save ~USD1.00, or the pins used as serial RX/TX instead).
* Six spare GPIOs on a 2 x 5 block of holes at the top edge, with GND and two switched 3.3V, for a header if ever needed.
* Test pads on every supply rail (VBUS, VBAT, VSYS, 3V3, 3V3_SW, 3V3_RF) and GND, labelled on the board.
* 37mm * 84mm board with connectors mostly at the ends, so that it can fit inside a 40mm pipe as an affordable enclosure.

## Antennas

Neither antenna is on the board or in `BOM.csv` (which is generated from the schematic) — buy them separately.

**Never transmit without the LoRa antenna connected**: the SX1262's output stage can be damaged driving an open socket.

The LoRa antenna plugs into the U.FL (IPEX MHF1) socket on the Ra-01SH. It must be a **50 Ω antenna for the
sub-GHz band** the board is configured for — 868 MHz (EU, Kenya, and 865–867 MHz India) or 915 MHz (Australia,
AS923 Indonesia). A 2.4 GHz WiFi antenna fits the same socket but works badly; the ESP32's own U.FL socket is
2.4 GHz, so label the two cables. Antennas marked "868/915" or "860–930 MHz" cover every region at some cost in
gain. When buying SMA parts, check SMA versus RP-SMA: they look alike and don't mate.

### Regular node

| Option | Parts | When |
|---|---|---|
| Whip through the end cap (recommended) | U.FL (MHF1) to SMA-female bulkhead pigtail, ~10–15 cm, 1.13 mm coax; 2–3 dBi SMA-male whip for the band | Nodes that relay for others or are far from their neighbours — range is the point of LoRa |
| Flexible PCB antenna inside the pipe | Adhesive FPC antenna with a U.FL lead | Short hops; no hole in the enclosure; cheapest. Expect less range: small FPC antennas are inefficient, so use the largest that fits |

Keep the antenna in a plastic (not metal) pipe, as far from the WiFi antenna, the cell and any wet soil as
the enclosure allows, and vertical if possible (nodes and gateway should share the same polarisation).

### Gateway node

The gateway is the same board (DECISIONS L11), but its antenna matters more because every node's traffic
passes through it.

* An outdoor omni antenna — fibreglass, 3–6 dBi, N-type, for the band (or 860–930 MHz), mast-mounted.
* Height beats gain: a few metres up, clear of roofs and trees, gains more than a higher-gain antenna low down.
* Keep the coax short. Thin cable loses several dB per metre at 900 MHz, so put the board (in its pipe) on the
  mast next to the antenna with a short pigtail, and run power or USB to it rather than RF. If a long RF run
  is unavoidable use low-loss coax (LMR-400 class).
* Seal the outdoor connectors (self-amalgamating tape) and earth the mast.
* Gain counts against the legal limit. With the SX1262 at its full +22 dBm, a 5.8 dBi antenna gives about
  28 dBm EIRP: inside Australia's 915–928 MHz limit (1 W EIRP) but far over Europe's 868 MHz limit
  (about 25 mW ERP in most sub-bands). Check the local rules (Kenya, India, Indonesia each set their own)
  and turn TX power down in firmware to match.

### Where to buy (low cost)

AliExpress listings, prices in USD as seen from Australia on 1 Nov 2026 without new-shopper deals; shipping
varies. Listings change and sellers' gain claims are optimistic, so check before ordering.

| For | Listing | Price | Per board |
|---|---|---|---|
| Node whip, 915 MHz | [NOWEPOCH, 3 dBi whip + U.FL-to-SMA bulkhead pigtail, pack of 4](https://www.aliexpress.com/item/1005008182646662.html) | 7.18 / 4 (6.35 at ≥10 packs) | 1.59–1.80 |
| Node whip, 868/915 MHz | [XYANT, 3 dBi whip + U.FL-to-SMA 15 cm pigtail, pack of 4](https://www.aliexpress.com/item/1005008633276903.html) | 7.79 / 4 (6.86 at ≥10 packs) | 1.72–1.95 |
| Node internal, 915 MHz | [CDEBYTE (Ebyte) TX915-FPC, 2.5 dBi, 10 per lot; sizes 3009, 4510, 7020, 8521 (length × width, mm)](https://www.aliexpress.com/item/1005010384153076.html) | 3.69–5.79 / 10 | 0.37–0.58 |
| Gateway antenna, 868 or 915 MHz | [GIZONT fibreglass omni, 35 cm, N-type, "5.8 dBi" (choose band variant)](https://www.aliexpress.com/item/1005012560449111.html) | 6.40–6.54 | — |
| Gateway pigtail | [U.FL (IPX1) to waterproof N-female bulkhead, RG178, 5 cm to 2 m](https://www.aliexpress.com/item/1005004546386028.html) | 3.60 (8 cm) | — |

Notes:
* For comparison, [Rokland's MHF1-to-SMA pigtails](https://store.rokland.com/products/2-pack-ufl-ipex4-mhf4-to-sma-female-pigtail-antenna-wifi-iot-dev-cable) alone are about USD 4 per board.
* The 868/915 whip is a compromise across both bands; the 915-only one should do a little better in AU/AS923.
* No 868 MHz version of the Ebyte FPC was found on AliExpress; for 868 regions use the whip, or find an 868 FPC.
  Choose the 8521 (85 × 21 mm) size if it fits — bigger is more efficient at sub-GHz.
* A real 5.8 dBi collinear at 868 MHz is usually much longer than 35 cm; treat the GIZONT as roughly 3 dBi.
  It is still a cheap, weatherproof outdoor antenna. Better-documented ones ([RAK](https://www.aliexpress.com/item/32852314761.html), [SparkFun](https://www.sparkfun.com/lora-fiberglass-antenna-type-n-5-8dbi-863-870mhz.html)) cost USD 40–120.
* RG178 loses roughly 1 dB per metre or more at 900 MHz: keep the gateway pigtail as short as the mounting allows.

## Software features

The board can be flashed with any software, but its designed to work well with [Frugal-IoT](https://github.com/mitra42/frugal-iot) which has the following features.

* Support for a very wide and expanding range of sensors
* Integrates with Frugal-IoT cloud, and UX on phone or laptop
* Plug and play MQTT interface, treats remote sensors and actuators the same as local ones
* LoRa mesh (using [LoRaMesher](https://github.com/LoRaMesher/LoRaMesher)), so sensors out of WiFi range report through other boards; any board can be the gateway to WiFi.
* Captive WiFi portal for local configuration
* Local controls for on-device automation configured through the UX.
* Multilingual support on both captive portal and UX
* Automatic Over-The-Air (OTA) updates for unattended devices (when on WiFi)
* Power management for really long life for sensors that report at long intervals.
* mDNS, for device to device signalling when the Internet is down
* NTP integration for accurate clock
* Fully Open-Source (i.e. not crippleware)

The radio is wired to the same ESP32-S3 pins as the Heltec WiFi LoRa 32 V3/V4, so firmware set up for those boards carries over.

## Files

| | |
|---|---|
| `SCHEMATIC.pdf` | schematic, one sheet |
| `BOM.csv` | bill of materials with LCSC (JLCPCB) part numbers; DNP = not fitted |
| `COST-ESTIMATE.txt` | JLCPCB cost for 10 and 100 boards, and the saving without Modbus |
| `PCB-LAYOUT.pdf` | 3D views and both copper layers |
| `fabrication/` | files to order from JLCPCB — see its README |
| `DECISIONS.md` | requirements, design decisions and why |
| `datasheets/` | Ai-Thinker Ra-01SH specification (Chinese; pinout, footprint and internal schematic) |
| `frugal_iot_v03/` | KiCad 10 project |
| `v0.2-baseline/` | the V0.2 board this started from: its README, decisions, schematic, layout, BOM, fabrication and firmware files |
| `claude-tools/` | scripts Claude uses to regenerate the design — reviewers can ignore |

The schematic is generated from `claude-tools/schematic/circuit.py`: changes made by Claude go there, not into
the .kicad_sch. Regenerate: `buildlib.py`, `run_draw_bg.sh` (log must end `VERIFY OK`), `run_kicad.sh`,
then `jlc_dump.sh` and `python3 cost_estimate.py > ../../COST-ESTIMATE.txt`.

If the fabrication and KiCad directories are not available wherever you find this, please let me know (mitra@mitra.biz) and I'll send you them.
