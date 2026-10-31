"""KiCad python, one-off clean-up of the V0.3 routed board (L19):
- remove the first hand-routed VBUS link under the USB-C (it sat on J1's locating-peg holes) and add the
  re-routed one from out/route_fix_VBUS.json (route/astar.py with J1's NPTH holes as obstacles);
- remove dangling vias and a GND via too close to the module's thermal-pad holes;
- test points: clear 'exclude from BOM' so the footprints match their symbols."""
import json, pcbnew
PCB = '../../frugal_iot_v03/frugal_iot_v03.kicad_pcb'
b = pcbnew.LoadBoard(PCB); mm = pcbnew.FromMM; t = pcbnew.ToMM; V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))
near = lambda p, x, y, d=0.05: abs(t(p.x) - x) < d and abs(t(p.y) - y) < d
kill = []
old_vias = [(69.7, 80.9), (74.6, 80.7), (58.67, 74.01), (62.93, 71.43), (67.95, 59.95)]
old_ends = [(69.7, 80.0), (69.7, 80.9), (71.3, 82.2), (73.1, 82.2), (74.6, 80.7), (74.6, 80.1)]
for tr in list(b.GetTracks()):
    if tr.GetClass() == 'PCB_VIA':
        if any(near(tr.GetPosition(), x, y) for x, y in old_vias): kill.append(tr)
    elif tr.GetNetname() == 'VBUS':
        s, e = tr.GetStart(), tr.GetEnd()
        if any(near(s, x, y) for x, y in old_ends) and any(near(e, x, y) for x, y in old_ends): kill.append(tr)
tps = [f for f in b.GetFootprints() if f.GetReference().startswith('TP')]
d = json.load(open('out/route_fix_VBUS.json')); net = b.FindNet(d['net'])
for k in kill: b.Remove(k)
for f in tps: f.SetAttributes(f.GetAttributes() & ~pcbnew.FP_EXCLUDE_FROM_BOM)
for L, x0, y0, x1, y1 in d['segs']:
    if abs(x0 - x1) < 1e-6 and abs(y0 - y1) < 1e-6: continue
    tr = pcbnew.PCB_TRACK(b); tr.SetStart(V(x0, y0)); tr.SetEnd(V(x1, y1)); tr.SetWidth(mm(d['width']))
    tr.SetLayer(pcbnew.F_Cu if L == 'F.Cu' else pcbnew.B_Cu); tr.SetNet(net); b.Add(tr)
for x, y in d['vias']:
    v = pcbnew.PCB_VIA(b); v.SetPosition(V(x, y)); v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); b.Add(v)
pcbnew.SaveBoard(PCB, b)
print('removed', len(kill), 'added', len(d['segs']), 'segs', len(d['vias']), 'vias; TPs', len(tps))
