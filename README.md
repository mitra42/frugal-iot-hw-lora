# Frugal-IoT V0.3 (LoRa)

Frugal-IoT V0.2 — a simple, multi-purpose sensor board with onboard charging and an external antenna — plus
an SX1262 LoRa radio, so boards can mesh with each other where there's no WiFi.

**Status:** requirements agreed (30 Oct 2026). See `DECISIONS.md` for the requirements,
decisions (ESP32-S3-WROOM-1U + Ai-Thinker Ra-01SH) and the one open question (power). No schematic or layout yet.

Forked from [frugal-iot-hw-sensor](https://github.com/mitra42/frugal-iot-hw-sensor) (V0.2).

## Files

| | |
|---|---|
| `DECISIONS.md` | V0.3 requirements, proposed decisions and open questions |
| `v0.2-baseline/` | V0.2 as forked: its README, decision log, schematic, layout, BOM, cost estimate, fabrication and firmware files |
| `frugal_iot_v02/` | V0.2's KiCad 10 project — the starting point; to be renamed when V0.3 work starts |
| `claude-tools/` | scripts Claude uses to regenerate the design — reviewers can ignore |
