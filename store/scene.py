"""57store's original night-shift interior, drawn as editable pixel geometry.

The room is a portrait RPG cutaway: ground recedes vertically; fixtures have
visible tops, standing faces and contact shadows. References inform structure,
not the brand's eight-colour charcoal / mint visual language.
"""
from html import escape
from pathlib import Path
import re
import runpy

INK='#0a0b0c'; DARK='#131415'; DEEP='#25292b'; STEEL='#50595c'
SAGE='#879393'; PALE='#bdc7c5'; WHITE='#e0e6e2'; MINT='#53efc0'
W,H=640,1960


def position(item):
    x,y,w,h=item['bounds']; minimum=48 if item.get('small') else 88
    if min(x,y)<0 or w<minimum or h<minimum or x+w>W or y+h>H:
        raise ValueError('Invalid store hit area: '+item['id'])
    return f'left:{x/W*100:g}%;top:{y/H*100:g}%;width:{w/W*100:g}%;height:{h/H*100:g}%'


def render_entries(config):
    expected={'receipt':'/receipt/','sys':'/sys/','cctv':'/cctv/'}
    if len(config['entries'])!=3 or {e['id']:e['href'] for e in config['entries']}!=expected:
        raise ValueError('The store opens exactly receipt, sys and cctv')
    return ''.join(f'<a class="store-entry entry-{e["id"]}" data-store-object="{e["id"]}" style="{position(e)}" href="{e["href"]}"><span class="store-visually-hidden">{escape(e["label"])} / {escape(e["subtitle"])}</span></a>' for e in config['entries'])


def render_labels(config):
    result=[]; ids={e['id'] for e in config['entries']}
    for f in config['fixtures']:
        ident=f['id']
        if not re.fullmatch('[a-z]+',ident) or ident in ids:
            raise ValueError('Invalid or duplicate store fixture')
        ids.add(ident)
        result.append(f'<button type="button" hidden class="store-object object-{ident}" data-store-object="{ident}" data-small="{str(f.get("small",False)).lower()}" style="{position(f)}" aria-expanded="false" aria-controls="label-{ident}"><span class="store-visually-hidden">查看{escape(f["name"])}</span></button>')
        result.append(f'<div hidden class="shelf-label" id="label-{ident}" role="status"><strong>{escape(f["name"])}</strong><span>{escape(f["note"])}</span></div>')
    return ''.join(result)


def render_scene():
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" class="store-art" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true" focusable="false" shape-rendering="crispEdges">']
    eq=runpy.run_path(str(Path(__file__).with_name('equipment.py')))['render_equipment']
    fu=runpy.run_path(str(Path(__file__).with_name('furnishings.py')))['render_furnishing']
    def r(x,y,w,h,c,attr=''):p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {attr}/>')
    def path(d,c,attr=''):p.append(f'<path d="{d}" fill="{c}" {attr}/>')
    def g(ident=None,cls=None):p.append('<g'+(f' id="fixture-{ident}"' if ident else '')+(f' class="{cls}"' if cls else '')+'>')
    def end():p.append('</g>')
    def motion(cls):g(cls='ambient '+cls)
    def text(x,y,value,size=12,c=PALE,anchor='start'):
        p.append(f'<text x="{x}" y="{y}" font-family="Store Mono,monospace" font-size="{size}" text-anchor="{anchor}" fill="{c}" shape-rendering="auto">{escape(value)}</text>')
    def box(x,y,w,d,h=18,top=STEEL,front=DEEP):
        # Top plane, separate front thickness, and a short right return.
        path(f'M{x+6} {y+9}h{w+3}v{d+h}h{-w-3}z',INK,'opacity=".6"')
        r(x,y,w,d+h,INK);r(x+3,y+3,w-6,d-3,top)
        r(x+3,y+d,w-6,h-3,front);r(x+3,y+3,w-6,2,PALE)
        r(x+w-6,y+5,3,d+h-8,STEEL);r(x+4,y+d,w-10,2,SAGE)
    def wall(x,y,w):
        # y is the room-side ground contact. Wall height projects north.
        r(x+4,y+4,w,10,INK);r(x,y-27,w,35,DEEP)
        r(x,y-31,w,7,STEEL);r(x,y-31,w,2,PALE);r(x,y+5,w,3,STEEL)
    def vwall(x,y,h):
        r(x+9,y+4,9,h,INK);r(x,y,10,h,DEEP);r(x,y,4,h,SAGE);r(x+6,y,4,h,STEEL)
    def fixture(ident,kind,x,y,w,h,furniture=False):
        g(ident);p.append((fu if furniture else eq)(kind,x,y,w,h));end()
    def cup(x,y):
        path(f'M{x} {y+4}h17v15h-2v4h-12v-4h-3z',PALE)
        path(f'M{x+2} {y}h12v2h3v7h-3v2h-12v-2h-3V{y+2}h3z',WHITE)
        r(x+3,y+3,10,5,DEEP);r(x+17,y+8,5,9,STEEL);r(x+18,y+10,2,5,PALE)
    def carton(x,y,w=34,h=26):
        box(x,y,w,h,12,STEEL,DEEP);r(x+w//2-2,y+3,4,h-3,SAGE)
        r(x+5,y+7,12,8,PALE);r(x+7,y+9,8,2,STEEL)
    def bottle(x,y):
        r(x+4,y,7,4,PALE);r(x+3,y+4,9,4,SAGE)
        path(f'M{x+3} {y+8}h9l3 4v17H{x}V{y+12}z',STEEL)
        r(x+2,y+15,11,8,PALE);r(x+5,y+17,6,3,DEEP);r(x+2,y+10,2,5,WHITE)
    def person(x,y,kind,coat=SAGE):
        # A compact original operator, with crown, small face, coat and feet.
        p.append(f'<g transform="translate({x} {y})">');motion(kind)
        path('M-4 41h34v10H-4z',INK,'opacity=".65"')
        g(cls='feet');r(3,37,8,12,INK);r(18,37,8,12,INK);r(3,46,10,3,STEEL);r(18,46,10,3,STEEL);end()
        path('M3 20h23v4h4v19H0V25h3z',coat);r(5,23,4,16,STEEL);r(22,24,3,16,DEEP)
        g(cls='hand');r(-5,26,7,13,coat);r(-5,37,7,5,PALE);end()
        r(29,27,6,12,coat);r(29,37,6,5,PALE)
        path('M5 1h18v3h4v17h-4v4H6v-4H2V5h3z',INK)
        r(7,3,14,4,STEEL);r(5,6,18,8,DEEP);r(7,14,17,9,PALE);r(8,14,3,5,INK)
        r(14,17,2,2,INK);r(22,17,2,2,INK)
        if kind in ('clerk','restocker'):r(19,27,6,3,WHITE)
        elif kind=='reader':
            g(cls='hand');r(28,29,24,19,INK);r(29,30,10,16,PALE);r(41,30,10,16,WHITE)
            r(31,33,6,3,STEEL);r(43,34,6,2,DEEP);r(43,39,6,1,STEEL);end()
        else:
            r(33,35,18,15,STEEL);r(33,35,18,3,SAGE);r(36,31,12,2,PALE)
            for xx in (36,41,46):r(xx,40,2,6,DEEP)
        end();end()
    def roomdoor(ident,x,y,w=65):
        g(ident);r(x,y-26,w,34,INK)
        # Open leaf is parked beside the wall, not across the usable floor.
        r(x+w-7,y+3,7,66,STEEL);r(x+w-6,y+4,2,61,PALE);r(x+w-3,y+48,5,4,MINT);end()

    # Charcoal is the dominant ground. No coloured floor wash or explanatory text.
    r(12,18,612,H-30,INK);r(23,28,591,H-53,DARK)
    for yy in range(130,H-30,48):r(30,yy,576,1,DEEP)
    for xx in range(36,610,48):r(xx,132,1,H-168,DEEP)
    vwall(20,30,H-51);vwall(606,30,H-51)
    # Front wall / glazing belongs to the shop, with the door above the welcome mat.
    g('sign');wall(29,93,577);motion('sign-light');r(36,63,562,3,MINT);end();end()
    for xx,ww in ((32,208),(443,161)):
        r(xx,95,ww,33,INK);r(xx+3,98,ww-6,24,STEEL);r(xx+4,99,ww-8,2,PALE)
        for xxx in range(xx+24,xx+ww-4,40):r(xxx,99,2,23,SAGE)
    g('door');r(245,88,195,51,INK)
    for cls,xx in (('door-left',249),('door-right',343)):
        motion(cls);r(xx,93,92,37,STEEL);r(xx+3,96,86,27,DEEP);r(xx+3,96,86,2,PALE);r(xx+5,114,82,3,MINT);end()
    r(247,134,191,4,PALE);r(251,140,184,3,INK);end()
    g('mat');r(245,165,232,120,INK);r(249,169,224,112,DEEP)
    r(256,175,210,2,STEEL);r(256,273,210,2,STEEL)
    text(361,200,'57STORE',23,MINT,'middle');text(361,216,'ゴナナストア',12,PALE,'middle')
    text(361,234,'每日生活、本地缓存。',13,WHITE,'middle')
    text(361,250,'Daily Life, Local Cache.',12,PALE,'middle')
    text(361,266,'暮らし、ローカルキャッシュ。',12,PALE,'middle');end()
    # A bounded cashier workspace: back equipment, working aisle, front counter.
    r(32,142,200,228,DEEP);r(33,142,5,228,STEEL)
    fixture('warmers','warmer',39,146,94,91);fixture('prep','microwave',138,147,94,91)
    g('clerk');person(149,239,'clerk',MINT);end()
    fixture('receipt','checkout',32,280,201,143)
    fixture('magazines','magazines',487,153,116,177)
    g('reader');person(438,191,'reader',STEEL);end()
    g('camera');r(567,96,4,28,STEEL);r(553,115,19,5,STEEL)
    motion('camera-swivel');box(543,114,29,13,10,PALE,STEEL);r(541,124,6,9,INK);end();end()
    g('baskets');box(432,343,46,26,21,STEEL,DEEP)
    r(438,349,34,14,INK)
    for xx in range(440,470,6):r(xx,351,2,11,SAGE)
    for yy in (366,371,376):r(436,yy,38,2,SAGE)
    end()
    g('umbrella');box(532,345,49,27,33,DEEP,STEEL)
    for xx,yy in ((540,321),(551,314),(565,323)):
        r(xx,yy,3,41,PALE);path(f'M{xx} {yy}v-7h10v8h-3v-5h-4v4z',SAGE)
    end()
    # The public floor: three compact islands and equipment anchored to perimeter walls.
    fixture('coffee','coffee',34,441,128,179)
    g('bins')
    for xx in (36,102):
        box(xx,647,51,32,43,STEEL,DEEP);r(xx+7,653,37,22,PALE);r(xx+14,659,23,12,INK)
        r(xx+11,690,29,12,SAGE);r(xx+15,693,20,2,DEEP)
    end()
    fixture('snacks','snacks',226,442,190,221,True)
    fixture('fresh','fresh',485,443,120,223)
    fixture('dairy','dairy',34,754,128,198)
    fixture('noodles','noodles',226,754,190,220,True)
    fixture('bento','bento',485,754,120,220)
    g('shopper');person(174,807,'shopper',PALE);end()
    fixture('freezer','freezer',33,1047,134,117)
    fixture('bread','bread',225,1053,194,154,True)
    fixture('daily','daily',485,1051,120,156,True)
    g('special');box(34,1181,115,27,26,STEEL,DEEP)
    for xx in (42,69,96,123):
        r(xx,1184,19,22,PALE);r(xx+3,1186,13,15,SAGE);r(xx+5,1189,9,10,WHITE)
    end()

    # WC has a real rear installation wall. The door is offset to its right.
    r(32,1290,180,283,DEEP)
    for yy in range(1297,1570,24):r(36,yy,172,1,STEEL)
    wall(30,1286,114);wall(205,1286,14);vwall(211,1286,291)
    roomdoor('toiletdoor',145,1286,63)
    fixture('toilet','toilet',38,1272,104,157,True)
    # Paper and controls are at the seated person's SIDE, fixed to the west wall.
    g('toiletpaper');r(33,1390,17,9,STEEL);r(36,1387,12,11,PALE);r(38,1397,10,12,WHITE)
    r(33,1362,12,17,DEEP);r(35,1364,8,4,MINT)
    path('M37 1416v37h12','none',f'stroke="{SAGE}" stroke-width="4"');end()
    g('toiletbasin');box(163,1504,48,27,21,PALE,STEEL);r(169,1511,35,14,SAGE);r(175,1513,23,9,DEEP)
    path('M185 1513v-15h10v8h-3v-5h-4v12z',WHITE);r(202,1497,8,11,MINT)
    r(200,1469,10,30,STEEL);r(202,1472,6,22,PALE);r(203,1474,2,17,WHITE);end()
    wall(30,1577,189)
    roomdoor('staffdoor',220,1286,65)
    # The drink wall is a room boundary, with one compact replenishment aisle behind.
    fixture('drinks','drinks',287,1245,318,151)
    r(286,1396,320,181,DARK)
    for yy in (1430,1478,1526):r(292,yy,307,1,DEEP)
    vwall(281,1396,76);vwall(281,1559,18);wall(284,1577,323)
    g('walkin');box(294,1401,191,31,26,STEEL,DEEP)
    for xx in range(301,475,19):bottle(xx,1404)
    end()
    g('fan');box(544,1400,51,25,17,STEEL,DEEP)
    p.append('<g transform="translate(568 1414)">');motion('fan-spin')
    path('M-3-3h6v-9h5v6h-5v9h9v5h-6v-5h-9v9h-5v-6h5v-9h-9v-5h6z',PALE)
    end();end();r(566,1412,4,4,INK);end()
    g('colddoor');r(281,1473,9,84,INK);r(291,1475,67,10,PALE);r(295,1477,57,3,WHITE);r(348,1484,6,5,STEEL);end()
    fixture('coldstock','stockrack',500,1465,100,90,True)
    g('restocker');person(401,1490,'restocker',STEEL);end()

    # ONE compact back workplace. Storage and systems share walls; no extra office/rest floors.
    r(32,1589,574,339,DARK)
    for yy in range(1613,1920,48):r(33,yy,570,1,DEEP)
    fixture('stock','stockrack',34,1588,132,173,True)
    fixture('sys','sysdesk',270,1558,110,110,True)
    fixture('cctv','cctvdesk',388,1558,110,110,True)
    g('receiving');box(35,1794,96,42,20,STEEL,DEEP);carton(44,1798,51,27)
    r(43,1858,10,7,INK);r(113,1858,10,7,INK);path('M119 1794v-23h8v31h-8z',PALE);end()
    g('cleaning');box(149,1805,44,41,56,STEEL,DEEP)
    r(152,1853,36,38,DEEP);r(178,1862,4,12,SAGE);r(153,1893,33,2,INK)
    # Chemical storage is enclosed, distinct from the wash-up counter.
    r(155,1810,28,27,DEEP);r(158,1815,11,18,SAGE);r(160,1811,6,4,PALE);end()
    g('staffwork');box(216,1830,112,42,41,STEEL,DEEP)
    g('handsink');r(221,1835,35,28,PALE);r(227,1840,23,16,DEEP)
    path('M235 1869v-19h9v8h-3v-5h-3v16z',WHITE);end()
    g('wash');r(263,1836,29,27,PALE);r(267,1840,21,17,DEEP);path('M278 1869v-17h8v7h-3v-4h-2v14z',WHITE);end()
    g('foodprep');r(299,1836,23,27,SAGE);r(301,1840,19,20,PALE);cup(302,1838)
    motion('prep-steam');path('M309 1843v-8h3v-6h-3v-8h3v-6h3v9h-3v6h3v13z',WHITE,'opacity=".6"');end();end()
    # The visible south surface is the cabinet BACK; its doors face the north aisle.
    r(222,1881,100,2,STEEL);end()
    g('staffbreak');box(346,1844,122,31,29,STEEL,DEEP)
    path('M357 1816h25v4h4v37h-4v4h-25v-4h-4v-37h4z',STEEL);r(358,1823,24,32,PALE);r(362,1825,3,25,WHITE);r(362,1813,17,5,INK);r(381,1827,7,19,INK)
    cup(407,1836);r(441,1818,19,24,PALE);r(445,1814,11,4,STEEL)
    motion('break-steam');path('M414 1835v-7h3v-7h-3v-7h3v-5h3v8h-3v7h3v11z',WHITE,'opacity=".7"');end()
    # A folding stool in front of the wall counter, rather than a separate dining room.
    box(388,1778,44,21,18,STEEL,DEEP);r(392,1817,5,12,INK);r(423,1817,5,12,INK);end()
    fixture('lockers','lockers',506,1558,96,145,True)
    g('clock');r(194,1560,31,25,INK);r(198,1563,23,17,PALE)
    p.append('<g transform="translate(209 1572)">');motion('clock-hand');r(0,-6,1,7,INK);end();end();end()
    wall(21,1930,595)
    p.append('</svg>');return ''.join(p)
