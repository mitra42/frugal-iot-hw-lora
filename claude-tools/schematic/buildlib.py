"""Write frugal_iot_v03/frugal.kicad_sym (rail power symbols VSYS, VBAT, +3V3_SW, +3V3_RF; XB5353A; Ra-01SH) and
frugal_iot_v03/frugal.pretty/Ai-Thinker-Ra-01SH.kicad_mod, plus the project fp-lib-table."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import dumps, Str
from customsyms import _prop, _pin, _sym, _rect
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'frugal_iot_v03', 'frugal.kicad_sym')
t = open(os.path.join(os.environ.get('KICAD10_SYMBOL_DIR', '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'), 'power.kicad_sym')).read()
m = re.search(r'\n\t\(symbol "\+3V3"\n', t); i = m.start() + 1
d = 0; j = i; ins = False
while True:
    c = t[j]
    if ins:
        if c == '\\': j += 2; continue
        if c == '"': ins = False
    elif c == '"': ins = True
    elif c == '(': d += 1
    elif c == ')':
        d -= 1
        if d == 0: break
    j += 1
tmpl = t[i:j + 1]
blocks = []
for name in ('VSYS', 'VBAT', '+3V3_SW', '+3V3_RF'):
    blocks.append(tmpl.replace('"+3V3"', f'"{name}"').replace('"+3V3_0_1"', f'"{name}_0_1"')
                  .replace('"+3V3_1_1"', f'"{name}_1_1"').replace('\\"+3V3\\"', f'\\"{name}\\"'))
# XB5353A (XySemi): one-cell Li-ion protection with integrated MOSFETs, SOT-23-5.
# Pins per datasheet (LCSC C80628): 1 VT (test, leave open), 2 GND (cell -), 3 VDD (cell +), 4/5 VM (pack -).
pins = [_pin('3', 'VDD', 'power_in', -7.62, 2.54, 0), _pin('2', 'GND', 'passive', -7.62, -2.54, 0),
        _pin('4', 'VM', 'passive', 7.62, 2.54, 180), _pin('5', 'VM', 'passive', 7.62, -2.54, 180),
        _pin('1', 'VT', 'passive', 0, 7.62, 270)]
props = [_prop('Reference', 'U', 0, 7.62 + 1.27), _prop('Value', 'XB5353A', 0, -6.35),
         _prop('Footprint', 'Package_TO_SOT_SMD:SOT-23-5', 0, 0, True), _prop('Datasheet', '~', 0, 0, True),
         _prop('Description', 'XySemi XB5353A one-cell Li-ion protection IC with integrated MOSFETs (3 A discharge OC, 4.30/2.4 V), SOT-23-5', 0, 0, True)]
xb = _sym('XB5353A', props, _rect(-5.08, -5.08, 5.08, 5.08), pins)
blocks.append('\t' + dumps(xb, 1))
# Ai-Thinker Ra-01SH (SX1262 LoRa, 803-930 MHz). Pins per Ai-Thinker Ra-01SH specification V1.1, table 4.
L = [('15', 'NSS', 'input'), ('12', 'SCK', 'input'), ('14', 'MOSI', 'input'), ('13', 'MISO', 'output'),
     ('4', 'RESET', 'input'), ('10', 'BUSY', 'output'), ('6', 'DIO1', 'bidirectional')]
Rt = [('1', 'ANT', 'passive'), ('5', 'TXEN', 'passive'), ('11', 'RXEN', 'passive'), ('7', 'DIO2', 'bidirectional'),
      ('8', 'DIO3', 'bidirectional')]
top = 2.54 * 4; pins = []
for k, (n, nm, ty) in enumerate(L): pins.append(_pin(n, nm, ty, -12.7, top - 2.54 * (k + 1), 0))
for k, (n, nm, ty) in enumerate(Rt): pins.append(_pin(n, nm, ty, 12.7, top - 2.54 * (k + 1), 180))
pins.append(_pin('3', '3V3', 'power_in', 0, top + 5.08, 270))
for k, n in enumerate(('2', '9', '16')): pins.append(_pin(n, 'GND', 'power_in' if k == 0 else 'passive', 0, top - 2.54 * 9, 90, hide=k > 0))
props = [_prop('Reference', 'U', 0, top + 7.62), _prop('Value', 'Ra-01SH', 0, top - 2.54 * 10),
         _prop('Footprint', 'frugal:Ai-Thinker-Ra-01SH', 0, 0, True),
         _prop('Datasheet', 'https://docs.ai-thinker.com/en/lora', 0, 0, True),
         _prop('Description', 'Ai-Thinker Ra-01SH SX1262 LoRa module, 803-930 MHz, SPI, IPEX antenna socket; TXEN = DIO2 inside the module, RXEN not connected', 0, 0, True)]
blocks.append('\t' + dumps(_sym('Ra-01SH', props, _rect(-10.16, top + 2.54, 10.16, top - 2.54 * 8), pins), 1))
out = '(kicad_symbol_lib\n\t(version 20251024)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "10.0")\n' + '\n'.join(blocks) + '\n)\n'
open(OUT, 'w').write(out)
print('wrote', OUT, len(out))

# ---- footprint: Ai-Thinker Ra-01SH, 16 x 17 mm, 2 x 8 castellated pads at 2.0 mm pitch ----
# Pads per the spec's recommended land pattern: module pads 1.27 x 1.0 at the 16.06 mm edges; ours run from the
# module pad's inner end (6.75 mm from centre) 0.7 mm beyond its edge, as the spec allows (outward only).
# Pin 1 (ANT) top-left; 1-8 down the left, 9-16 up the right (top view), as the Ra-01.
PRETTY = os.path.join(HERE, '..', '..', 'frugal_iot_v03', 'frugal.pretty'); os.makedirs(PRETTY, exist_ok=True)
def line(x1, y1, x2, y2, layer, w):
    return f'\t(fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (layer "{layer}"))\n'
fp = ['(footprint "Ai-Thinker-Ra-01SH" (version 20260206) (generator "frugal-buildlib") (layer "F.Cu")\n',
      '\t(descr "Ai-Thinker Ra-01SH SX1262 LoRa module, 16x17 mm, SMD16 stamp holes, 2.0 mm pitch")\n',
      '\t(tags "LoRa SX1262 Ra-01SH")\n',
      '\t(property "Reference" "REF**" (at 0 -10 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n',
      '\t(property "Value" "Ra-01SH" (at 0 10 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n',
      '\t(attr smd)\n']
W, H = 8.0, 8.5
for a, b, c, d in ((-W, -H, W, -H), (W, -H, W, H), (W, H, -W, H), (-W, H, -W, -H)):
    fp.append(line(a, b, c, d, 'F.Fab', 0.1))
for a, b, c, d in ((-8.1, -8.6, 8.1, -8.6), (-8.1, 8.6, 8.1, 8.6), (-8.1, -8.6, -8.1, -7.9), (8.1, -8.6, 8.1, -7.9),
                   (-8.1, 8.6, -8.1, 7.9), (8.1, 8.6, 8.1, 7.9)):
    fp.append(line(a, b, c, d, 'F.SilkS', 0.12))
fp.append('\t(fp_poly (pts (xy -9.3 -7.5) (xy -9.3 -6.5) (xy -8.8 -7)) (stroke (width 0.1) (type solid)) (fill yes) (layer "F.SilkS"))\n')
for a, b, c, d in ((-9.0, -9.0, 9.0, -9.0), (9.0, -9.0, 9.0, 9.0), (9.0, 9.0, -9.0, 9.0), (-9.0, 9.0, -9.0, -9.0)):
    fp.append(line(a, b, c, d, 'F.CrtYd', 0.05))
for k in range(8):
    y = -7 + 2 * k
    for n, x in ((k + 1, -7.75), (16 - k, 7.75)):
        fp.append(f'\t(pad "{n}" smd roundrect (at {x} {y}) (size 2.0 1.0) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.25))\n')
fp.append(')\n')
open(os.path.join(PRETTY, 'Ai-Thinker-Ra-01SH.kicad_mod'), 'w').write(''.join(fp))
open(os.path.join(HERE, '..', '..', 'frugal_iot_v03', 'fp-lib-table'), 'w').write(
    '(fp_lib_table\n\t(version 7)\n\t(lib (name "frugal")(type "KiCad")(uri "${KIPRJMOD}/frugal.pretty")(options "")(descr "Project footprints"))\n)\n')
print('wrote footprint + fp-lib-table')
