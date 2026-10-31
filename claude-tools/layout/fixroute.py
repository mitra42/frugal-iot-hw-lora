"""KiCad python: import a Freerouting session into the pre-route board (as prep_route.py left it), plus any
hand-completed connections as route_fix_*.json from route/astar.py, and save. Usage: fixroute.py out/routed.ses [fix.json ...]
(V0.3: the astar fixes were already folded into the session by route/fix2ses.py, so no json is passed.)"""
import sys, json, pcbnew
PCB = '../../frugal_iot_v03/frugal_iot_v03.kicad_pcb'
b = pcbnew.LoadBoard(PCB)          # the board as prep_route.py left it (GND fan-out, keepouts)
print('import', pcbnew.ImportSpecctraSES(b, sys.argv[1]))
mm = pcbnew.FromMM; V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))
for fx in sys.argv[2:]:
    d = json.load(open(fx)); net = b.FindNet(d['net'])
    for L, x0, y0, x1, y1 in d['segs']:
        if abs(x0 - x1) < 1e-6 and abs(y0 - y1) < 1e-6: continue
        t = pcbnew.PCB_TRACK(b); t.SetStart(V(x0, y0)); t.SetEnd(V(x1, y1)); t.SetWidth(mm(d['width']))
        t.SetLayer(pcbnew.F_Cu if L == 'F.Cu' else pcbnew.B_Cu); t.SetNet(net); b.Add(t)
    for x, y in d['vias']:
        v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); b.Add(v)
    print('added', d['net'], len(d['segs']), 'segments', len(d['vias']), 'vias')
pcbnew.SaveBoard(PCB, b)
