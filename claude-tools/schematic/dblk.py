"""Drawing blocks for Frugal-IoT V0.3 LoRa (schlib). Parts and nets come from circuit.py via dbase."""
import dbase as B
from dbase import tag as dbtag, pwr_pin, side, put, put_pin, pin, port, drop, term, hang, rise, series, diode_r, at


def lab_up(ref, node, net, top, length=5.08):
    """Pull-up style: `ref` stands on `node` to rail `top`; net label hangs below node."""
    S = B.S
    rise(ref, node, top, bottom_pin='2')
    S.wire(node, at(node, 0, length)); S.label(net, node[0], node[1] + length, angle=270)


def lab_down(ref, node, net, bottom, length=5.08):
    """Pull-down/filter style: `ref` hangs from `node` to `bottom`; net label stands above node."""
    S = B.S
    hang(ref, node, bottom)
    S.wire(node, at(node, 0, -length)); S.label(net, node[0], node[1] - length, angle=90)


# ------------------------------------------------------------------ USB-C
def usb(x, y):
    S = B.S
    with S.block("USB-C: 5 V IN AND PROGRAMMING"):
        put('J1', x, y)
        vb = pin('J1', 'A4')
        n1 = at(vb, 7.62)
        S.wire(vb, n1)
        nf = at(n1, 0, -2.54)
        S.wire(n1, nf, at(nf, 0, -2.54)); port('VBUS', *at(nf, 0, -2.54))
        S.wire(nf, at(nf, -5.08)); S.power('PWR_FLAG', nf[0] - 5.08, nf[1])
        term('J1', 'SH', 'GND')
        ga = pin('J1', 'A1'); gq = at(ga, 0, 2.54); S.wire(ga, gq, at(gq, 0, 2.54)); port('GND', *at(gq, 0, 2.54))
        S.wire(gq, at(gq, 7.62)); S.power('PWR_FLAG', gq[0] + 7.62, gq[1])
        S.nc('J1', 'A8', 'B8')
        term('J1', 'A5', 'CC1', 2.54)
        term('J1', 'B5', 'CC2', 2.54)
        # join the flipped pairs; D- (A7/B7) above D+ (A6/B6)
        pa, pb = pin('J1', 'A7'), pin('J1', 'B7')
        xj = pa[0] + 2.54
        S.wire(pa, (xj, pa[1])); S.wire(pb, (xj, pb[1])); S.wire((xj, pa[1]), (xj, pb[1]))
        qa, qb = pin('J1', 'A6'), pin('J1', 'B6')
        S.wire(qa, (xj, qa[1])); S.wire(qb, (xj, qb[1])); S.wire((xj, qa[1]), (xj, qb[1]))
        S.wire((xj, pb[1]), (xj + 7.62, pb[1])); S.label('USB_D_N', xj + 7.62, pb[1])
        S.wire((xj, qa[1]), (xj + 7.62, qa[1])); S.label('USB_D_P', xj + 7.62, qa[1])
        # CC pull-downs
        cx = n1[0] + 30.48
        for ref, net in (('R1', 'CC1'), ('R2', 'CC2')):
            top = (cx, vb[1] - 15.24)
            S.wire(top, at(top, 0, -2.54)); S.label(net, top[0], top[1] - 2.54, angle=90)
            hang(ref, top, 'GND')
            cx += 10.16
        # J6: 2-way terminal beside the USB-C for external 5 V wiring (D10)
        put('J6', cx + 10.16, vb[1] + 20.32)
        term('J6', '1', 'VBUS', 15.24)
        term('J6', '2', 'GND', 5.08)
        S.note("USB-C sink, 5 V only: CC1/CC2 5.1k to GND. D+/D- go straight to the S3's native USB\n"
               "(GPIO20/GPIO19): no USB-UART chip and no ESD chip (D9).\n"
               "J6: XY308-2P screw terminal for external 5 V, e.g. a solar panel (D10; fitted from D34).",
               x - 5.08, y + 33.02, 1.0)


# ------------------------------------------------------------------ charger + protection
def charger(x, y):
    S = B.S
    with S.block("LI-ION CHARGER & CELL PROTECTION"):
        put('U1', x, y)
        v = pin('U1', '4')
        mid = at(v, 0, -5.08); topp = at(v, 0, -7.62)
        S.wire(v, mid, topp); port('VBUS', *topp)
        c1 = at(mid, -20.32)
        S.wire(mid, c1); hang('C1', c1, 'GND')
        ce = pin('U1', '8'); S.wire(ce, at(ce, -5.08), at(ce, -5.08, -5.08)); port('VBUS', *at(ce, -5.08, -5.08))
        term('U1', '7', 'nCHRG', 5.08); term('U1', '6', 'nSTDBY', 5.08)
        g3, g9 = pin('U1', '3'), pin('U1', '9')
        S.wire(g9, at(g9, 0, 2.54), at(g3, 0, 2.54)); S.wire(g3, at(g3, 0, 2.54), at(g3, 0, 5.08)); port('GND', *at(g3, 0, 5.08))
        # BAT -> VBAT rail above the IC
        b = pin('U1', '5')
        ry = b[1] - 10.16
        b1 = at(b, 7.62)
        S.wire(b, b1, (b1[0], ry))
        r = [b1[0] + 7.62, b1[0] + 15.24, b1[0] + 30.48]
        S.wire((b1[0], ry), *[(xx, ry) for xx in r])
        hang('C2', (r[0], ry), 'GND')
        drop('VBAT', (r[1], ry), 2.54)
        # J4 cell connector (fitted from D34): pin 1 = cell -, pin 2 = cell +
        put_pin('J4', '2', (r[2] + 5.08, ry), mirror='y')
        S.wire((r[2], ry), pin('J4', '2'))
        term('J4', '1', 'CELL_NEG', 2.54)
        # TEMP grounded (no cell NTC)
        t = pin('U1', '1')
        e = at(t, 33.02)
        S.wire(t, e, at(e, 0, 5.08)); port('GND', *at(e, 0, 5.08))
        # PROG: 4.7k fixed, second 4.7k via JP1 for 500 mA
        p = pin('U1', '2')
        p1 = at(p, 7.62); p2 = at(p, 20.32)
        S.wire(p, p1, p2)
        hang('R3', p1, 'GND')
        m = hang('R4', p2)
        put_pin('JP1', '1', m, rot=270)
        assert pin('JP1', '2')[1] > m[1]
        term('JP1', '2', 'GND')
        # charge LEDs (open-drain outputs, lit from VBUS)
        for k, (rr, dd, net) in enumerate((('R5', 'D1', 'nCHRG'), ('R6', 'D2', 'nSTDBY'))):
            s0 = (x - 45.72, y + 22.86 + 10.16 * k)
            tp = at(s0, -2.54)
            S.wire(tp, s0); port('VBUS', *tp)
            e2 = series(rr, s0)
            kk = diode_r(dd, e2)
            S.wire(kk, at(kk, 2.54)); S.label(net, kk[0] + 2.54, kk[1])
        # ---- protection: XB5353A in the cell's negative lead ----
        px, py = x + 7.62, y + 48.26
        put('U2', px, py)
        vdd = pin('U2', '3')
        n = at(vdd, -5.08)
        S.wire(vdd, n, at(n, 0, -5.08)); port('VBAT', *at(n, 0, -5.08))
        c = at(n, -10.16)
        S.wire(n, c)
        cb = hang('C3', c)
        S.wire(cb, at(cb, 0, 2.54)); S.label('CELL_NEG', cb[0], cb[1] + 2.54, angle=270)
        g = pin('U2', '2')
        S.wire(g, at(g, -2.54), at(g, -2.54, 5.08)); S.label('CELL_NEG', g[0] - 2.54, g[1] + 5.08, angle=270)
        p4, p5 = pin('U2', '4'), pin('U2', '5')
        e4, e5 = at(p4, 5.08), at(p5, 5.08)
        S.wire(p4, e4); S.wire(p5, e5); S.wire(e4, e5)
        S.wire(e5, at(e5, 0, 2.54)); port('GND', *at(e5, 0, 2.54))
        S.nc('U2', '1')
        S.note("PROG: I = 1200 / R. 4.7k = 255 mA (default); bridge JP1 (2.35k) = 510 mA (D8).\n"
               "TEMP grounded: no cell thermistor. J4 (JST-PH, fitted from D34): pin 1 = cell -,\n"
               "pin 2 = cell +. Not all JST-PH cells are wired the same way: check polarity (D11).\n"
               "XB5353A (D12) sits in the cell's negative lead: board GND is the pack's P-.\n"
               "Trips at 4.30 V / 2.4 V, 3 A discharge; C3 at its VDD pin.",
               x - 45.72, y - 27.94, 1.0)


# ------------------------------------------------------------------ system power
def syspwr(x, y):
    S = B.S
    with S.block("SYSTEM POWER: LOAD SHARING, 3.3 V LDO, SWITCHED SENSOR RAIL"):
        a = (x, y)
        drop('VBUS', a, 2.54)
        k = diode_r('D3', at(a, 5.08)); S.wire(a, at(a, 5.08))
        ry = k[1]
        xs = [k[0] + 7.62, k[0] + 20.32, k[0] + 27.94]
        S.wire(k, *[(xx, ry) for xx in xs])
        # load-sharing P-FET below the rail: S up to VSYS, D down to VBAT, gate = VBUS
        put_pin('Q1', '2', (xs[0], ry + 2.54), mirror='x')
        S.wire((xs[0], ry), pin('Q1', '2'))
        term('Q1', '3', 'VBAT', 2.54)
        gp = pin('Q1', '1')
        gn = (a[0], gp[1])
        S.wire(a, gn, gp)
        hang('R7', gn, 'GND')
        hang('C4', (xs[1], ry), 'GND')
        S.wire((xs[1], ry), at((xs[1], ry), 0, -2.54)); S.power('PWR_FLAG', xs[1], ry - 2.54)
        dbtag('VSYS', (xs[1] - 5.08, ry), up=True, length=5.08)
        # LDO
        put_pin('U3', '1', (xs[2] + 7.62, ry))
        S.wire((xs[2], ry), pin('U3', '1'))
        en = pin('U3', '3')
        S.wire(en, (en[0] - 2.54, en[1]), (en[0] - 2.54, ry))
        term('U3', '2', 'GND'); S.nc('U3', '4')
        vo = pin('U3', '5')
        o = [vo[0] + 5.08, vo[0] + 12.7]
        S.wire(vo, *[(xx, vo[1]) for xx in o])
        hang('C5', (o[0], vo[1]), 'GND')
        drop('+3V3', (o[1], vo[1]), 2.54)
        # battery sense divider
        bx, by = o[1] + 15.24, ry - 5.08
        S.wire((bx, by), at((bx, by), 0, -2.54)); port('VBAT', bx, by - 2.54)
        m = hang('R8', (bx, by))
        hang('R9', m, 'GND')
        c = at(m, 7.62); S.wire(m, c); hang('C6', c, 'GND')
        S.wire(c, at(c, 5.08)); S.label('VBAT_SENSE', c[0] + 5.08, c[1])
        # switched sensor rail: P-FET, gate pulled up to +3V3 (off), GPIO5 low = on
        sx, sy = x + 20.32, y + 38.1
        put('Q2', sx, sy, mirror='x')
        assert pin('Q2', '2')[1] < pin('Q2', '3')[1]
        term('Q2', '2', '+3V3', 2.54)
        d = pin('Q2', '3')
        d1 = at(d, 0, 2.54); d2 = at(d1, 10.16)
        S.wire(d, d1, at(d1, 5.08), d2)
        hang('C7', at(d1, 5.08), 'GND')
        drop('+3V3_SW', d2, 2.54)
        S.wire(d2, at(d2, 7.62)); S.power('PWR_FLAG', d2[0] + 7.62, d2[1])
        g = pin('Q2', '1')
        gn = at(g, -5.08)
        S.wire(g, gn)
        rise('R10', gn, '+3V3', bottom_pin='2')
        S.wire(gn, at(gn, 0, 5.08)); S.label('nRAIL_EN', gn[0], gn[1] + 5.08, angle=270)
        # test points (L20): one per supply rail, plus GND for the probe's ground
        for i in range(7):
            ref = f'TP{i + 1}'
            net = B.PARTS[ref]['value']
            # pad drawn below its rail (rail symbol upright); the GND pad hangs above its ground symbol
            put_pin(ref, '1', (x + 76.2 + 10.16 * i, y + 43.18), rot=0 if net == 'GND' else 180)
            term(ref, '1', net, 2.54)
        S.note("D3 + Q1: with USB present VSYS comes through D3 and Q1 is off; without it Q1 turns on\n"
               "and the cell feeds VSYS. The charger never carries the load.\n"
               "U3 RT9080 (L18): 600 mA, 2 uA quiescent. VBAT_SENSE = VBAT / 2 (1M/1M, ~2 uA).\n"
               "Q2: nRAIL_EN (GPIO15) LOW = +3V3_SW on. R10 holds the rail off through reset and boot.\n"
               "TP1-TP7: probe pads on VBUS, VBAT, VSYS, +3V3, +3V3_SW, +3V3_RF and GND (L20).",
               x - 5.08, y + 58.42, 1.0)


# ------------------------------------------------------------------ module
def pullup_sw(rref, swref, net, x, y):
    """+3V3 -> R -> node(label) -> switch -> GND, drawn as one vertical column."""
    S = B.S
    n = (x, y)
    rise(rref, n, '+3V3', bottom_pin='2')
    put_pin(swref, '1', at(n, 0, 2.54), rot=270)
    assert pin(swref, '2')[1] > n[1]
    S.wire(n, pin(swref, '1'))
    term(swref, '2', 'GND')
    S.wire(n, at(n, -5.08)); S.label(net, n[0] - 5.08, n[1], angle=180)


def signals(ref, skip=()):
    """Stub every signal pin of `ref` to its net label (or a no-connect), from circuit.py."""
    S = B.S
    for (r, k) in B.NO_CONNECT:
        if r == ref and k not in skip: S.nc(ref, k)
    for net, nodes in B.NETS.items():
        if net in B.RAIL: continue
        for r, k in nodes:
            if r == ref and k not in skip: term(ref, k, net, 5.08)


def module(x, y):
    S = B.S
    with S.block("ESP32-S3-WROOM-1U MODULE"):
        put('U4', x, y)
        signals('U4')
        v = pin('U4', '2')
        m = at(v, 0, -17.78); t = at(v, 0, -20.32)
        S.wire(v, m, t); port('+3V3', *t)
        S.wire(m, at(m, 10.16), at(m, 17.78))
        hang('C8', at(m, 10.16), 'GND'); hang('C9', at(m, 17.78), 'GND')
        term('U4', '1', 'GND')                      # pins 1, 40 and 41 (pad) share one point
        sx = x - 81.28
        # reset: pull-up + RC + button
        n = (sx, y - 25.4)
        rise('R11', n, '+3V3', bottom_pin='2')
        S.wire(n, at(n, 7.62)); hang('C10', at(n, 7.62), 'GND')
        put_pin('SW1', '1', at(n, 0, 2.54), rot=270); S.wire(n, pin('SW1', '1')); term('SW1', '2', 'GND')
        S.wire(n, at(n, -5.08)); S.label('EN', n[0] - 5.08, n[1], angle=180)
        # BOOT on GPIO0
        pullup_sw('R12', 'SW2', 'BOOT', sx, y + 2.54)
        # status LED on GPIO21 (active low; not a strapping pin), J7 for an off-board LED
        n = (sx + 20.32, y + 2.54)
        a = at(n, 10.16, -20.32)
        S.wire(a, at(a, 0, -2.54)); port('+3V3', a[0], a[1] - 2.54)
        put_pin('R13', '1', a); r2 = pin('R13', '2')
        put_pin('D4', '2', at(r2, 0, 2.54), rot=90)
        assert pin('D4', '1')[1] > r2[1]
        S.wire(r2, pin('D4', '2'))
        kk = pin('D4', '1')
        S.wire(kk, (kk[0], n[1]), n)
        S.wire(n, at(n, 0, 5.08)); S.label('STATUS_LED', n[0], n[1] + 5.08, angle=270)
        put_pin('J7', '1', at(r2, 20.32), mirror='y')
        S.wire(r2, pin('J7', '1'))
        term('J7', '2', 'STATUS_LED', 2.54)
        S.note("GPIO map (L3, L19): sensors 4/5 (ADC1) -> J2, spares 1/2 (ADC1) -> J13, VBAT_SENSE 6, I2C 17/18,\n"
               "LoRa NSS/SCK/MOSI/MISO 8-11, RST 12, BUSY 13, DIO1 14 (as Heltec V3/V4), nRAIL_EN 15,\n"
               "RS485 DE 38, UART0 43/44 -> RS485 or J3, USB 19/20, LED 21, BOOT 0.\n"
               "Spares 36, 39, 41, 42, 47, 48 -> J5 holes (L10, L19). Not connected: straps 3, 45, 46 (internal defaults)\n"
               "and 7, 16, 35, 37, 40. J7 (not fitted): off-board LED, pin 1 = anode, pin 2 = cathode, shares R13.\n"
               "C8/C9 close to module pin 2. U.FL antenna: module end at the board edge, away from the LoRa antenna (L5).",
               x - 81.28, y + 45.72, 1.0)


# ------------------------------------------------------------------ connectors
RL = {'GND': 12.7, '+3V3_SW': 22.86}   # rail stub lengths: keep power symbols clear of the labels

def conn(x, y):
    S = B.S
    with S.block("SENSOR CONNECTORS J2, J3 (FITTED) AND SPARE GPIO HOLES J5"):
        # I2C pull-ups (on +3V3_SW: nothing back-powers sensors when the rail is off)
        lab_up('R14', (x, y), 'I2C_SDA', '+3V3_SW')
        lab_up('R15', (x + 12.7, y), 'I2C_SCL', '+3V3_SW')
        # sensor input options (not fitted)
        lab_up('R16', (x, y + 30.48), 'SENS1', '+3V3_SW')
        lab_up('R17', (x + 12.7, y + 30.48), 'SENS2', '+3V3_SW')
        lab_down('C11', (x + 25.4, y + 33.02), 'SENS1', 'GND')
        lab_down('C12', (x + 38.1, y + 33.02), 'SENS2', 'GND')
        # J2 = J2A (pins 1-5) + J2B (pins 6-10)
        jx = x + 76.2
        nets = {'J2': ['GND', 'I2C_SDA', 'I2C_SCL', '+3V3_SW', 'GND'],
                'J12': ['SENS1', '+3V3_SW', 'GND', 'SENS2', '+3V3_SW'],
                'J3': ['GND', 'J3_P2', 'J3_P3', '+3V3_SW', 'GND'],
                'J13': ['GPIO1', '+3V3_SW', 'GND', 'GPIO2', '+3V3_SW']}
        for i, ref in enumerate(('J2', 'J12')):
            put(ref, jx, y - 2.54 + 17.78 * i)
            for k, net in enumerate(nets[ref]):
                term(ref, str(k + 1), net, RL.get(net, 2.54))
        for i, ref in enumerate(('J3', 'J13')):
            put(ref, jx + 45.72, y - 2.54 + 17.78 * i)
            for k, net in enumerate(nets[ref]):
                term(ref, str(k + 1), net, RL.get(net, 2.54))
        # J3 pins 2/3: UART (default, bridged 1-2) or RS485 A/B (cut, bridge 2-3)
        for i, (ref, a, c, b) in enumerate((('JP2', 'RS485_A', 'J3_P2', 'RXD0'), ('JP3', 'RS485_B', 'J3_P3', 'TXD0'))):
            put(ref, jx + 7.62 + 30.48 * i, y + 50.8)
            term(ref, '1', a, 5.08); term(ref, '3', b, 5.08); term(ref, '2', c, 2.54)
        # J5: spare GPIOs on unfitted holes (L10)
        put('J5', jx + 91.44, y + 12.7)
        signals('J5')
        term('J5', '1', 'GND', RL['GND']); term('J5', '2', '+3V3_SW', RL['+3V3_SW']); term('J5', '6', '+3V3_SW', RL['+3V3_SW'])
        S.note("J2 (main) and J3 share one layout, pins 1-10 (D4, D5); J2, J12, J3 and J13 all fitted (J2: S1/S2 = GPIO4/5, J3: GPIO1/2):\n"
               "  1 GND  2 SDA/A  3 SCL/B  4 3V3_SW  5 GND  6 S1/GPIO1  7 3V3_SW  8 GND  9 S2/GPIO2  10 3V3_SW\n"
               "Each is two XY308-2.54-5P blocks side by side (no 10-way part at JLCPCB): J2+J12, J3+J13.\n"
               "JP2/JP3: J3 pins 2-3 = RS485 A/B as delivered; cut 1-2 and bridge 2-3 for UART0 RX/TX (U5 must then be left off) (D29).\n"
               "J5: holes only, no connector (L10): spare GPIO 36, 39, 41, 42, 47, 48, GND on 1, 3V3_SW on 2 and 6, 4 not connected and 3V3_SW. R16 (SENS1 pull-up) and C12 (SENS2 filter) fitted; R17, C11 not fitted.\n"
               "Firmware: switch +3V3_SW on (GPIO15 low) before any I2C or sensor access.",
               x - 5.08, y + 76.2, 1.0)


# ------------------------------------------------------------------ RS485 option
def rs485(x, y):
    S = B.S
    with S.block("RS485 / MODBUS (FITTED; OMIT TO SAVE COST)"):
        put('U5', x, y)
        term('U5', '1', 'RXD0', 5.08); term('U5', '4', 'TXD0', 5.08)
        p2, p3 = pin('U5', '2'), pin('U5', '3')
        j2, j3 = at(p2, -2.54), at(p3, -2.54)
        S.wire(p2, j2); S.wire(p3, j3); S.wire(j2, j3)
        S.wire(j3, at(j3, -5.08)); S.label('RS485_DE', j3[0] - 5.08, j3[1], angle=180)
        v = pin('U5', '8')
        m = at(v, 0, -7.62); t = at(v, 0, -10.16)
        S.wire(v, m, t); port('+3V3_SW', *t)
        S.wire(m, at(m, -10.16)); hang('C13', at(m, -10.16), 'GND')
        term('U5', '5', 'GND')
        term('U5', '6', 'RS485_A', 5.08); term('U5', '7', 'RS485_B', 5.08)
        # DE/RE pull-down, bias, termination, surge protection
        bx = x + 40.64
        lab_down('R18', (x - 30.48, y + 25.4), 'RS485_DE', 'GND')
        lab_up('R19', (bx, y), 'RS485_A', '+3V3_SW')
        lab_down('R20', (bx + 12.7, y + 2.54), 'RS485_B', 'GND')
        st = (bx - 5.08, y + 25.4)
        S.wire(at(st, -5.08), st); S.label('RS485_A', st[0] - 5.08, st[1], angle=180)
        e = series('R21', st)
        S.wire(e, at(e, 2.54))
        series('JP4', at(e, 2.54), first='1', rot=0)
        term('JP4', '2', 'RS485_B', 5.08)
        put('D5', bx + 30.48, y + 7.62)
        term('D5', '1', 'RS485_A', 5.08); term('D5', '2', 'RS485_B', 5.08); term('D5', '3', 'GND')
        S.note("Fitted by default: J3 pin 2 = A, pin 3 = B via JP2/JP3 (D29). A board without Modbus can leave out\n"
               "U5, C13, R18-R21, D5 and J3 (see COST-ESTIMATE.txt). GPIO38 = DE/RE (high = transmit, R18 = receive).\n"
               "JP4 bridged = 120R termination. RS485 sensors need their own 5-24 V supply (external).",
               x - 30.48, y + 35.56, 1.0)


# ------------------------------------------------------------------ LoRa radio
def lora(x, y):
    S = B.S
    with S.block("LORA RADIO: AI-THINKER RA-01SH (SX1262)"):
        put('U6', x, y)
        signals('U6')
        v = pin('U6', '3')
        m = at(v, 0, -15.24); t = at(v, 0, -17.78)
        S.wire(v, m, t); port('+3V3_RF', *t)
        S.wire(m, at(m, 10.16), at(m, 17.78))
        hang('C14', at(m, 10.16), 'GND'); hang('C15', at(m, 17.78), 'GND')
        term('U6', '2', 'GND')                      # pins 2, 9 and 16 share one point
        lab_up('R22', (x - 40.64, y + 10.16), 'LORA_NSS', '+3V3_RF')
        lab_up('R23', (x - 27.94, y + 10.16), 'LORA_RST', '+3V3_RF')
        # the radio's own regulator U7 (L18), drawn left of the pull-ups
        lx, ly = x - 104.14, y - 7.62
        a = (lx, ly)
        drop('VSYS', a, 2.54)
        hang('C16', at(a, 5.08), 'GND'); S.wire(a, at(a, 5.08))
        put_pin('U7', '1', at(a, 15.24))
        S.wire(at(a, 5.08), pin('U7', '1'))
        en = pin('U7', '3')
        S.wire(en, (en[0] - 2.54, en[1]), (en[0] - 2.54, ly))
        term('U7', '2', 'GND'); S.nc('U7', '4')
        vo = pin('U7', '5')
        S.wire(vo, at(vo, 7.62)); drop('+3V3_RF', at(vo, 7.62), 2.54)
        S.note("Ra-01SH (L2): SX1262 with crystal, 803-930 MHz, IPEX socket for the antenna (pad 1 ANT unused).\n"
               "The module drives its own RF switch from DIO2 (TXEN = DIO2 inside; RXEN not connected), so\n"
               "TXEN, RXEN, DIO2 and DIO3 are left open. Own always-on regulator U7 (+3V3_RF, L18): isolates the\n"
               "radio from WiFi load steps; LoRaMesher sleeps it over SPI, never by power. C14/C15 at pin 3, C16 at U7.\n"
               "R22 keeps the radio deselected and R23 keeps it out of reset while the ESP32 boots or sleeps.\n"
               "Firmware: LoRaMesher/RadioLib defaults fit (DC-DC regulator, no TCXO, DIO2 as RF switch) (L6).",
               x - 104.14, y + 35.56, 1.0)
