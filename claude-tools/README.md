# claude-tools — how Claude regenerates and changes this design

Reviewers can ignore this folder. Same method and scripts as the V0.2 board (frugal-iot-hw-sensor); everything
KiCad runs on Mitra's Mac with KiCad 10, the routing in the cloud. `out/` folders are scratch.

## Schematic — `schematic/`
Generated: edit `circuit.py` (parts, values, LCSC numbers, nets) and `dblk.py` (drawing), never the .kicad_sch.
`buildlib.py` (project symbols: VSYS/VBAT/+3V3_SW/+3V3_RF rails, XB5353A, Ra-01SH; Ra-01SH footprint) → `run_draw_bg.sh` (log ends `VERIFY OK`)
→ `run_kicad.sh` (ERC, netlist, ../../SCHEMATIC.pdf, ../../BOM.csv) → `jlc_dump.sh` + `python3 cost_estimate.py
> ../../COST-ESTIMATE.txt`.

## PCB — `layout/`
**Small changes after a schematic edit: KiCad "Update PCB from Schematic", re-route the affected nets, then
`fab.sh`.** The full rebuild below discards all routing.
- Fabrication: `fab.sh` → `python3 jlc_files.py` (→ ../../fabrication/); `renders.sh` for PCB-LAYOUT.pdf views.
- Full rebuild: `pipeline.sh 60` (fpmeasure → place → build_pcb → netclasses → DRC); `prep_route.py` → `dsn_prep.py`
  → Freerouting 2.1.0 via `route/Route.java` (cloud, Java 21) → `route/check_ses.py` → copy to `out/routed.ses`
  → `post_route.sh` → `island_pads.py` + `rescue.py REF:PAD,...` / `via_near.py REF:PAD` for any GND pad left
  in a detached pour island → `pinnum.py`, `addtext.py` → `fab.sh`.

## V0.3 routing (31 Oct 2026, DECISIONS L19)
`pipeline.sh 84 0.7` → `prep_route.py` (now also adds 0.35 mm edge keepouts) → `dsn_prep.py` → in the cloud,
`route/loop.sh board_r.dsn <tag> 6 30` (Freerouting, each result merged back with `route/merge.py` as the start
of the next run) → `route/astar.py` for what's left (folded into the session with `route/fix2ses.py`) →
`fixroute.py out/routed.ses` → `NOIMPORT=1 post_route.sh` → `patch_v03.py`, `prune.py NET...`, `islands2.py --fix`,
`rescue.py REF:PAD,...` → `polarity.py`, `pinnum.py`, `backtitle.py`, `backlabels.py`, `silk.py` → `fab.sh`,
`jlc_files.py`, `renders.sh` (PCB-LAYOUT.pdf assembled from the renders in the cloud).
