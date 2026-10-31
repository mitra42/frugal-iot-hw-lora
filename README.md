# Frugal-IoT V0.3 LoRa

A simple, un-opinionated, multi-purpose sensor board, that can be wired to sensors using most common interfaces (I2C, ModBus, OneWire, Analog) with onboard charging and external antennas, plus a LoRa radio so boards can talk to each other where there is no WiFi.

This is the [Frugal-IoT V0.2 sensor board](https://github.com/mitra42/frugal-iot-hw-sensor) with an SX1262 LoRa radio added.

**Status:** laid out and routed, for review (31 Oct 2026): 84 × 37 mm, DRC clean, JLCPCB files ready but not ordered. About USD17.31 per board for 10 and USD11.58 for 100. See `DECISIONS.md` for requirements, decisions and the one open question (power budget with LoRa).

## Hardware Features

* ESP32-S3-WROOM-1U
* Ai-Thinker Ra-01SH LoRa radio (SX1262, 803–930 MHz), so one board covers AU915, AS923, IN865 and EU868 — the band is set in firmware.
* Two U.FL sockets for external antennas, one for WiFi and one for LoRa.
* LoRa radio on its own always-on regulator, isolated from WiFi load and sleeping at under 1µA.
* USB-C for power and programming (e.g. using a $10 security camera solar panel)
* Protected charger circuitry for a single LiPo cell (~250mA), will work with really small cells (e.g. salvaged from vapes) or by adding a solder bridge can charge an 18650 cell at ~500mA
* Low-quiescent regulators (2µA each), so the board draws very little while asleep.
* Sensors controlled by a switched 3.3V sensor rail, allowing much lower power consumption in sleep.
* I2C support on J2
* Two sensor inputs on J2 (pins 6 & 9, GPIO4 & GPIO5) can be used for analog, OneWire etc, pads to add pull up resistor or smoothing capacitor if required.
* Two extra sensors on J3 (pins 6 & 9, GPIO1 & GPIO2)
* RS485(Modbus) on J3 pins 2 & 3, (can be omitted to save ~USD1.00, or the pins used as serial RX/TX instead).
* Six spare GPIOs on a 2 x 5 block of holes at the top edge, with GND and switched 3.3V, for a header if ever needed.
* Test pads on every supply rail (VBUS, VBAT, VSYS, 3V3, 3V3_SW, 3V3_RF) and GND, labelled on the board.
* 37mm * 84mm board with connectors mostly at the ends, so that it can fit inside a 40mm pipe as an affordable enclosure.

## Software features

The board can be flashed with any software, but its designed to work well with [Frugal-IoT](https://github.com/mitra42/frugal-iot) which has the following features.

* Support for a very wide and expanding range of sensors
* Integrates with Frugal-IoT cloud, and UX on phone or laptop
* Plug and play MQTT interface, treats remote sensors and actuators the same as local ones
* LoRa mesh (using [LoRaMesher](https://github.com/LoRaMesher/LoRaMesher)), so sensors out of WiFi range report through other boards; any board can be the gateway to WiFi.
* Captive WiFi portal for local configuration
* Local controls for on-device automation configured through the UX.
* Multilingual support on both captive portal and UX
* Automatic Over-The-Air (OTA) updates for unattended devices.
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
