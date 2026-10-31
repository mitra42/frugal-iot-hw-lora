"""Append an astar.py route_fix_*.json to a .ses (so later fixes and merge.py see it). Usage: fix2ses.py in.ses fix.json out.ses"""
import sys, json, re
s = open(sys.argv[1]).read(); f = json.load(open(sys.argv[2])); net = f['net']
add = ''
for L, x0, y0, x1, y1 in f['segs']:
    if abs(x0 - x1) < 1e-6 and abs(y0 - y1) < 1e-6: continue
    add += (f"\n        (wire\n          (path {L} {round(f['width'] * 10000)}\n            {round(x0 * 10000)} {round(-y0 * 10000)}\n"
            f"            {round(x1 * 10000)} {round(-y1 * 10000)}\n          )\n        )")
for x, y in f['vias']:
    add += f'\n        (via "Via[0-1]_600:300_um" {round(x * 10000)} {round(-y * 10000)}\n        )'
m = re.search(r"\n      \(net " + re.escape(net) + r"\n", s)
if not m: raise SystemExit('net not found in ses: ' + net)
k = m.end() - 1
s = s[:k] + add + s[k:]
open(sys.argv[3], 'w').write(s)
print('added', len(f['segs']), 'segs', len(f['vias']), 'vias to', net)
