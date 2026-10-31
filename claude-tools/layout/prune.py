"""KiCad python: remove dangling track chains (an end touching no pad, via or other track of its net on its
layer), for the nets given. Reads everything first, prunes in plain python, then mutates once (SWIG landmine).
Usage: prune.py NET [NET ...]"""
import sys, math, pcbnew
PCB = '../../frugal_iot_v03/frugal_iot_v03.kicad_pcb'
b = pcbnew.LoadBoard(PCB); T = pcbnew.ToMM
nets = set(sys.argv[1:])
objs = [t for t in b.GetTracks() if t.GetNetname() in nets]
segs = {}; vias = []
for i, t in enumerate(objs):
    if t.GetClass() == 'PCB_VIA':
        vias.append((t.GetNetname(), T(t.GetPosition().x), T(t.GetPosition().y), T(t.GetWidth()) / 2))
    else:
        segs[i] = (t.GetNetname(), t.GetLayer(), (T(t.GetStart().x), T(t.GetStart().y)), (T(t.GetEnd().x), T(t.GetEnd().y)), T(t.GetWidth()) / 2)
padhit = {}
for p in b.GetPads():
    if p.GetNetname() not in nets: continue
    for i, (n, L, a, c, w) in segs.items():
        if n != p.GetNetname() or not p.IsOnLayer(L): continue
        for k, q in ((0, a), (1, c)):
            if p.HitTest(pcbnew.VECTOR2I(pcbnew.FromMM(q[0]), pcbnew.FromMM(q[1]))): padhit[(i, k)] = True
def dseg(p, a, c):
    ax, ay = a; cx, cy = c; dx, dy = cx - ax, cy - ay; L2 = dx * dx + dy * dy
    u = 0 if L2 == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - u * dx, p[1] - ay - u * dy)
alive = set(segs); dead = set()
while True:
    new = set()
    for i in alive:
        n, L, a, c, w = segs[i]
        for k, q in ((0, a), (1, c)):
            if padhit.get((i, k)): continue
            if any(vn == n and math.hypot(vx - q[0], vy - q[1]) <= vr for vn, vx, vy, vr in vias): continue
            if any(j != i and segs[j][0] == n and segs[j][1] == L and dseg(q, segs[j][2], segs[j][3]) <= max(w, segs[j][4]) * 0.6 for j in alive): continue
            new.add(i); break
    if not new: break
    alive -= new; dead |= new
for i in dead: b.Remove(objs[i])
pcbnew.SaveBoard(PCB, b); print('pruned', len(dead))
