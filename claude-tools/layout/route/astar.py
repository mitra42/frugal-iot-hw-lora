"""Route one missing connection on a 2-layer board: grid A* over DSN pads + SES copper as obstacles
(V0.3: the connections Freerouting left; env CLR = clearance, HOLES = 'x,y,r;...' extra NPTH obstacles).
Usage: python3 astar.py board.dsn routed.ses NET width_mm board_width REF-PAD[,REF-PAD] -> out/route_fix_NET.json
(the pads named start the search; the rest of the net, pads and copper, is the goal)."""
import sys, re, math, heapq, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import dsnparse
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
dsn, ses, NET, W = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
import os
CLR = float(os.environ.get('CLR', 0.2)); VIA_R = 0.3; G = 0.1
pads, pin2net, cls = dsnparse.load(dsn)
SES_PER_MM = 10000.0
text = open(ses).read(); body = text[text.find('(network_out'):]
PATH = re.compile(r"\(path (\S+) (\d+)\n((?:\s+-?\d+ -?\d+\n)+)")
VIA = re.compile(r'\(via "([^"]+)"\s+(-?\d+)\s+(-?\d+)')
obs = {'F.Cu': [], 'B.Cu': []}; own = {'F.Cu': [], 'B.Cu': []}
for block in re.split(r"\n      \(net ", body)[1:]:
    name = block.split("\n", 1)[0].strip().strip('"')
    tgt = own if name == NET else obs
    for m in PATH.finditer(block):
        layer, w = m.group(1), int(m.group(2)) / SES_PER_MM
        pts = [(int(a) / SES_PER_MM, -int(b) / SES_PER_MM) for a, b in (l.split() for l in m.group(3).strip().split('\n'))]
        g = LineString(pts).buffer(w / 2) if len(pts) > 1 else Point(pts[0]).buffer(w / 2)
        tgt[layer].append(g)
    for m in VIA.finditer(block):
        c = Point(int(m.group(2)) / SES_PER_MM, -int(m.group(3)) / SES_PER_MM).buffer(0.3)
        for L in tgt: tgt[L].append(c)
# items of NET: (layers, geometry, label)
items = []
for L in ('F.Cu', 'B.Cu'):
    for g in own[L]: items.append(({L}, g, None))
for ref, num, layer, g in pads:
    n = pin2net.get(f'{ref}-{num}', '')
    layers = {'F.Cu', 'B.Cu'} if layer not in ('F.Cu', 'B.Cu') else {layer}
    for L in layers:
        if L in obs and n != NET: obs[L].append(g)
    if n == NET: items.append((layers & {'F.Cu', 'B.Cu'}, g, f'{ref}-{num}'))
# vias of NET appear in both own lists: merge duplicates by geometry identity is fine for union-find
par = list(range(len(items)))
def fd(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for a in range(len(items)):
    for b2 in range(a + 1, len(items)):
        if items[a][0] & items[b2][0] and items[a][1].distance(items[b2][1]) < 0.01:
            par[fd(a)] = fd(b2)
STARTS = set(sys.argv[6].split(','))
sroots = {fd(k) for k, it in enumerate(items) if it[2] in STARTS}
start = {'F.Cu': [], 'B.Cu': []}; goal = {'F.Cu': [], 'B.Cu': []}
for k, (ls, g, lab) in enumerate(items):
    for L in ls: (start if fd(k) in sroots else goal)[L].append(g)
# edge clearance
xs = [g.bounds for L in obs for g in obs[L]]
bx0, by0, bx1, by1 = 50.0, 50.0, 50.0 + float(sys.argv[5]), 87.0
for hx in filter(None, os.environ.get('HOLES', '').split(';')):     # NPTH holes (not in the DSN copper): x,y,r
    x_, y_, r_ = map(float, hx.split(',')); c_ = Point(x_, y_).buffer(r_)
    for L in obs: obs[L].append(c_)
trees = {L: STRtree(obs[L]) for L in obs}
allpads = [g for ref, num, layer, g in pads]; padtree = STRtree(allpads)
def via_ok(x, y):
    p = Point(x, y)
    return all(allpads[k].distance(p) >= VIA_R + 0.15 for k in padtree.query(p.buffer(VIA_R + 0.2)))
def clear(L, x, y, r):
    if not (bx0 + 0.3 + r <= x <= bx1 - 0.3 - r and by0 + 0.3 + r <= y <= by1 - 0.3 - r): return False
    p = Point(x, y)
    for i in trees[L].query(p.buffer(r + CLR)):
        if obs[L][i].distance(p) < r + CLR: return False
    return True
ut = {L: unary_union(start[L]) if start[L] else None for L in start}
gt = {L: unary_union(goal[L]) if goal[L] else None for L in goal}
def ingoal(L, x, y):
    return gt[L] is not None and gt[L].distance(Point(x, y)) < W / 2
starts = []
for L in ('F.Cu', 'B.Cu'):
    if ut[L] is None: continue
    b = ut[L].bounds
    for i in range(int((b[0] - 1) / G), int((b[2] + 1) / G) + 1):
        for j in range(int((b[1] - 1) / G), int((b[3] + 1) / G) + 1):
            x, y = i * G, j * G
            if ut[L].distance(Point(x, y)) < 0.05 and clear(L, x, y, W / 2): starts.append((L, i, j))
print('starts', len(starts), file=sys.stderr)
gc = {L: (gt[L].centroid.x, gt[L].centroid.y) for L in gt if gt[L] is not None}
def h(L, i, j):
    return min(math.hypot(i * G - cx, j * G - cy) for cx, cy in gc.values())
LY = ('F.Cu', 'B.Cu')
pq = []; came = {}; cost = {}
for s in starts:
    cost[s] = 0; heapq.heappush(pq, (h(*s), s))
cache = {}
def ok(L, i, j, r):
    k = (L, i, j, r)
    if k not in cache: cache[k] = clear(L, i * G, j * G, r)
    return cache[k]
found = None; n = 0
while pq:
    f, s = heapq.heappop(pq); n += 1
    L, i, j = s
    if ingoal(L, i * G, j * G): found = s; break
    if n > 2_000_000: break
    for di, dj in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        t = (L, i + di, j + dj); c = cost[s] + G * math.hypot(di, dj)
        if t not in cost or c < cost[t]:
            if ok(L, i + di, j + dj, W / 2):
                cost[t] = c; came[t] = s; heapq.heappush(pq, (c + h(*t), t))
    o = LY[1 - LY.index(L)]; t = (o, i, j); c = cost[s] + 6.0
    if (t not in cost or c < cost[t]) and ok(L, i, j, VIA_R) and ok(o, i, j, VIA_R) and via_ok(i * G, j * G):
        cost[t] = c; came[t] = s; heapq.heappush(pq, (c + h(*t), t))
print('expanded', n, 'found', found, file=sys.stderr)
if found:
    path = [found]
    while path[-1] in came: path.append(came[path[-1]])
    path.reverse()
    def seg_clear(L, a, b):
        ln = LineString([a, b]).buffer(W / 2)
        if not (bx0 + 0.3 <= min(a[0], b[0]) - W/2 and max(a[0], b[0]) + W/2 <= bx1 - 0.3 and by0 + 0.3 <= min(a[1], b[1]) - W/2 and max(a[1], b[1]) + W/2 <= by1 - 0.3): return False
        for k in trees[L].query(ln.buffer(CLR)):
            if obs[L][k].distance(ln) < CLR: return False
        return True
    runs = []; cur = [path[0]]
    for a, b in zip(path, path[1:]):
        if a[0] != b[0]: runs.append(cur); cur = [b]
        else: cur.append(b)
    runs.append(cur)
    segs = []; vias = []
    for r in runs:
        L = r[0][0]; pts = [(q[1] * G, q[2] * G) for q in r]
        k = 0; out = [pts[0]]
        while k < len(pts) - 1:
            m = len(pts) - 1
            while m > k + 1 and not seg_clear(L, pts[k], pts[m]): m -= 1
            out.append(pts[m]); k = m
        for a, b in zip(out, out[1:]): segs.append((L, a[0], a[1], b[0], b[1]))
    for a, b in zip(runs, runs[1:]): vias.append((a[-1][1] * G, a[-1][2] * G))
    json.dump(dict(net=NET, width=W, segs=segs, vias=vias), open(f'route_fix_{NET.strip("/")}.json', 'w'))
    print(json.dumps(dict(segs=segs, vias=vias)))
