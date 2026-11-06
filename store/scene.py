"""Original high-angle overhead pixel interior; 640 × 2660 authoring grid.

One parallel camera: ground axes remain X/Y; height projects toward north.
All objects are drawn from above, with top planes dominating short south lips.

Customer circulation is open. Insulated rear room supplies the drink display;
only the enclosed rear rooms and the inside of the counter are staff space.
"""
from html import escape
import random
import re
import runpy
from pathlib import Path

INK='#101b1a'; DARK='#20312e'; STEEL='#647e74'; PALE='#bdcdc0'
WHITE='#e0e8d7'; MINT='#50efc2'; SAGE='#8ba78d'; DEEP='#304d40'
W,H=640,2660


def position(item):
    x,y,w,h=item['bounds']
    minimum=48 if item.get('small') else 88
    if min(x,y)<0 or w<minimum or h<minimum or x+w>W or y+h>H:
        raise ValueError('Invalid store hit area: '+item['id'])
    return f'left:{x/W*100:g}%;top:{y/H*100:g}%;width:{w/W*100:g}%;height:{h/H*100:g}%'


def render_entries(config):
    expected={'receipt':'/receipt/','sys':'/sys/','cctv':'/cctv/'}
    if len(config['entries'])!=3 or {e['id']:e['href'] for e in config['entries']}!=expected:
        raise ValueError('The store opens exactly receipt, sys and cctv')
    return ''.join(f'<a class="store-entry entry-{e["id"]}" data-store-object="{e["id"]}" style="{position(e)}" href="{e["href"]}"><span class="store-visually-hidden">{escape(e["label"])} / {escape(e["subtitle"])}</span></a>' for e in config['entries'])


def render_labels(config):
    result=[];ids={e['id'] for e in config['entries']}
    for f in config['fixtures']:
        ident=f['id']
        if not re.fullmatch('[a-z]+',ident) or ident in ids:
            raise ValueError('Invalid or duplicate store fixture')
        ids.add(ident)
        result.append(f'<button type="button" hidden class="store-object object-{ident}" data-store-object="{ident}" data-small="{str(f.get('small', False)).lower()}" style="{position(f)}" aria-expanded="false" aria-controls="label-{ident}"><span class="store-visually-hidden">查看{escape(f["name"])}</span></button>')
        result.append(f'<div hidden class="shelf-label" id="label-{ident}" role="status"><strong>{escape(f["name"])}</strong><span>{escape(f["note"])}</span></div>')
    return ''.join(result)


def render_scene():
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" class="store-art" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true" focusable="false" shape-rendering="crispEdges">']
    rng=random.Random(57)
    equipment=runpy.run_path(str(Path(__file__).with_name('equipment.py')))['render_equipment']
    furniture=runpy.run_path(str(Path(__file__).with_name('furnishings.py')))['render_furnishing']
    def r(x,y,w,h,c,extra=''):
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>')
    def path(d,c,extra=''):
        p.append(f'<path d="{d}" fill="{c}" {extra}/>')
    def text(x,y,s,c=PALE,size=9,anchor='start'):
        p.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="Store Mono,monospace" font-size="{size}" text-anchor="{anchor}" shape-rendering="auto">{escape(s)}</text>')
    def g(ident=None,cls=None):
        p.append('<g'+(f' id="fixture-{ident}"' if ident else '')+(f' class="{cls}"' if cls else '')+'>')
    def end():p.append('</g>')
    def motion(name):g(cls='ambient '+name)
    def box(x,y,w,h,c=PALE,face=STEEL,d=12):
        path(f'M{x+8} {y+9}h{w}v{h+d}h{-w}z',INK,'opacity=".45"')
        r(x,y,w,h+d,INK);r(x+3,y+3,w-6,h-3,c);r(x+3,y+h,w-6,d-3,face)
        r(x+3,y+3,w-6,2,WHITE);r(x+w-5,y+5,2,h-5,STEEL)
    def line(x,y,w):
        r(x,y,w,4,STEEL);r(x,y,w,1,PALE)
        for xx in range(x+5,x+w-5,20):r(xx,y+1,8,2,WHITE)
    def bottle(x,y,c=MINT,scale=1):
        # Above the bottle: shoulder rim and cap, never a full upright label.
        p.append(f'<g transform="translate({x} {y}) scale({scale})">')
        path('M2 2h8l2 2v9l-2 2H2l-2-2V4z',INK)
        path('M3 3h6l2 2v6l-2 2H3l-2-2V5z',c)
        r(3,3,5,2,PALE);r(4,5,4,4,WHITE);r(5,6,2,2,STEEL);end()
    def pack(x,y,c=SAGE,kind='bag'):
        # Flat wrapping / a lid viewed from the same high camera as furniture.
        r(x,y+2,20,23,INK);r(x+2,y+2,16,19,c);r(x+3,y+3,14,2,WHITE)
        r(x+2,y+21,16,3,STEEL);r(x+6,y+8,9,7,PALE);r(x+8,y+10,5,3,DEEP)
        if kind=='bread':
            path(f'M{x+5} {y+7}h10v2h3v9h-3v2h-10v-2h-2v-9h2z',PALE)
            r(x+7,y+8,2,10,WHITE);r(x+12,y+8,2,10,WHITE)
    def carton(x,y,w=34,h=25):
        box(x,y,w,h,SAGE,DEEP,8);r(x+w//2-2,y+3,4,h-3,PALE);r(x+5,y+9,10,8,WHITE);r(x+7,y+11,6,2,STEEL)
    def person(x,y,kind,coat=PALE):
        # Crown, shoulders and hands. No frontal face / standing elevation.
        p.append(f'<g transform="translate({x} {y})">');motion(kind)
        path('M-4 14h34v20H-4z',INK,'opacity=".4"')
        g(cls='feet');r(4,28,7,7,INK);r(18,28,7,7,INK);end()
        path('M0 12h5V9h18v3h5v17H0z',coat)
        r(3,13,4,13,SAGE);r(21,13,4,13,STEEL)
        g(cls='hand');r(-5,17,8,6,coat);r(-8,17,5,6,PALE);end()
        r(26,17,8,6,coat);r(32,17,5,6,PALE)
        # The hair crown masks the torso, with one consistent north highlight.
        path('M8 1h12v3h5v15h-4v4H7v-4H3V5h5z',INK)
        r(8,3,12,3,DARK);r(7,6,5,3,STEEL);r(20,9,3,6,DARK)
        if kind in ('clerk','restocker'):r(19,25,6,3,WHITE)
        elif kind=='reader':
            g(cls='hand');r(25,21,24,20,INK);r(27,22,10,17,WHITE);r(38,22,10,17,PALE)
            r(37,23,1,16,STEEL);r(29,25,6,4,DEEP);r(40,26,6,2,SAGE);r(40,31,6,1,STEEL);end()
        else:
            r(31,27,18,12,DEEP);r(31,27,18,2,MINT);r(34,24,12,2,PALE)
            for xx in (34,39,44):r(xx,31,2,5,SAGE)
        end();end()
    def wall(x,y,w,h=10):
        r(x+4,y+8,w,h+7,INK,'opacity=".5"');r(x,y,w,h,STEEL);r(x,y,w,4,PALE)
    def device(ident,kind,x,y,w,h):
        g(ident);p.append(equipment(kind,x,y,w,h));end()
    def furnishing(ident,kind,x,y,w,h):
        g(ident);p.append(furniture(kind,x,y,w,h));end()
    def vwall(x,y,h):
        r(x+5,y+8,9,h,INK);r(x,y,10,h,STEEL);r(x,y,3,h,PALE)
    def door(ident,x,y,width=76,side='left'):
        g(ident);r(x,y,width,6,INK)
        leaf=x if side=='left' else x+width-7
        r(leaf,y+6,7,64,PALE);r(leaf+2,y+10,2,48,STEEL);r(leaf+5,y+53,4,4,MINT);end()
    # Continuous cutaway: no outdoor scenery and no explanatory floor lettering.
    r(8,18,624,H-26,INK);r(18,25,604,H-47,'#33443d')
    for yy in range(30,H-28,32):
        for xx in range(22,620,32):r(xx,yy,31,31,rng.choice(['#34453d','#35463e','#37483f']))
    r(20,30,8,H-50,PALE);r(28,30,4,H-50,STEEL)
    r(610,30,10,H-50,PALE);r(606,30,4,H-50,STEEL)
    path('M190 310h265v1020H190z',WHITE,'opacity=".035"')
    # The storefront is a cut wall viewed from above, not a front-facing banner.
    g('sign');r(30,24,580,15,INK);r(34,27,572,8,STEEL)
    motion('sign-light');r(37,28,566,3,PALE);r(40,35,560,3,MINT);end();end()
    r(34,42,572,63,'#284037')
    for xx in range(40,603,44):r(xx,45,2,55,'#3b5549')
    for xx,ww in ((32,211),(443,163)):
        r(xx,109,ww,29,INK);r(xx+4,112,ww-8,22,'#45695b');r(xx+5,114,ww-10,2,PALE)
        for k in range(xx+25,xx+ww-5,43):r(k,112,3,22,STEEL)
    g('door');r(246,107,194,42,INK);r(250,111,186,34,'#1b302a')
    for name,xx in [('door-left',250),('door-right',344)]:
        motion(name);r(xx,111,92,34,STEEL);r(xx+3,114,86,26,'#47675c');r(xx+3,115,85,2,PALE);r(xx+4,128,84,3,MINT);end()
    r(248,148,191,4,PALE);r(251,153,186,4,INK);r(334,108,14,4,MINT);end()
    # Brand and slogans are woven into a floor mat, aligned with the floor.
    g('mat');r(245,166,234,119,INK);r(249,170,226,111,'#234c3c')
    for yy in range(174,278,4):r(253,yy,218,1,'#2b5543')
    r(257,176,210,2,SAGE);r(257,273,210,2,SAGE)
    text(362,201,'57STORE',MINT,23,'middle')
    text(362,216,'ゴナナストア',PALE,12,'middle')
    text(362,234,'每日生活、本地缓存。',WHITE,13,'middle')
    text(362,250,'Daily Life, Local Cache.',PALE,12,'middle')
    text(362,266,'暮らし、ローカルキャッシュ。',PALE,12,'middle');end()
    # Checkout work aisle is enclosed on three sides, accessed on its right.
    r(34,148,194,173,'#28382e');r(35,152,6,170,STEEL)
    device('warmers','warmer',41,151,91,85)
    device('prep','microwave',139,152,94,86)
    g('clerk');person(147,252,'clerk',MINT);end()
    device('receipt','checkout',35,280,199,121)
    device('magazines','magazines',488,155,114,164)
    g('reader');person(447,195,'reader',SAGE);end()
    g('camera');r(565,111,4,24,STEEL);r(555,124,19,6,STEEL)
    motion('camera-swivel');path('M550 125h22v15h-22l-7-4v-7z',PALE);r(543,129,6,8,INK);r(552,127,6,2,WHITE);end();end()
    g('baskets')
    for yy in (320,324,328):
        r(431,yy,49,40,INK);r(434,yy+2,43,33,STEEL)
        r(439,yy+6,33,23,DEEP)
        for xx in range(442,469,6):r(xx,yy+8,2,19,SAGE)
        for row in (yy+12,yy+21):r(440,row,31,2,SAGE)
    r(435,326,40,2,PALE);end()
    g('umbrella');box(529,338,50,46,STEEL,DARK,7)
    r(535,345,38,31,DEEP)
    for xx,yy in ((539,350),(552,345),(562,358)):
        path(f'M{xx} {yy}h7l3 3v12l-3 3h-7l-3-3v-12z',PALE)
        r(xx+2,yy+2,2,9,WHITE);r(xx+3,yy+3,4,3,MINT)
    end()
    device('coffee','coffee',39,424,118,159)
    g('bins')
    for xx in (43,101):
        box(xx,613,48,70,STEEL,DARK,9)
        r(xx+4,617,40,61,PALE);r(xx+10,628,28,28,INK)
        path(f'M{xx+15} 631h18l4 4v13l-4 4h-18l-4-4v-13z',DEEP)
        r(xx+9,668,30,3,SAGE)
    end()
    # Larger single central gondolas retain two real circulation aisles.
    furnishing('snacks','snacks',224,431,186,229)
    furnishing('noodles','noodles',224,758,186,226)
    furnishing('bread','bread',224,1083,186,208)
    furnishing('daily','daily',484,1084,118,207)
    device('fresh','fresh',488,428,114,228)
    device('bento','bento',488,757,114,225)
    g('dairy');p.append(equipment('dairy',39,757,119,202));end()
    device('freezer','freezer',35,1039,126,111)
    g('special');box(43,1205,100,44,STEEL,DARK,13)
    for xx in (49,74,99,124):pack(xx,1209,PALE,'bread')
    r(47,1246,92,4,PALE);end()
    g('shopper');person(174,797,'shopper',PALE);end()
    # Toilet is reached from the PUBLIC rear cross-aisle, independently of staff.
    r(32,1374,162,288,'#66766b')
    for yy in range(1380,1660,20):
        for xx in range(36,192,20):r(xx,yy,19,19,'#768478')
    wall(30,1352,34);wall(151,1352,44);vwall(194,1352,314)
    door('toiletdoor',65,1352,85)
    # A human pictogram is fixed to the door, not written on the floor.
    r(68,1384,5,13,DEEP);r(68,1384,5,3,WHITE)
    furnishing('toilet','toilet',40,1432,108,144)
    g('toiletbasin');box(127,1584,54,37,PALE,STEEL,10);r(134,1591,37,22,STEEL);r(140,1596,26,12,INK)
    path('M149 1593v-16h13v9h-3v-6h-7v13z',WHITE);r(172,1577,9,13,MINT)
    r(132,1580,45,5,STEEL);r(136,1581,36,2,'#aac1b5');end()
    wall(30,1665,173)
    # A separate employee door leads to the service spine, never through WC.
    door('staffdoor',204,1352,74,'right')
    # Glass-door wall and the full, deep cold room behind it.
    r(282,1490,323,306,'#294238')
    for yy in range(1496,1788,24):r(287,yy,312,1,'#3b574b')
    device('drinks','drinks',283,1341,318,147)
    vwall(278,1490,131);vwall(278,1711,88);wall(281,1792,324)
    g('colddoor');r(279,1621,10,90,INK);r(289,1623,69,10,PALE);r(292,1625,58,3,WHITE);r(346,1631,7,4,STEEL);end()
    g('walkin');box(296,1511,292,51,STEEL,DEEP,12)
    for xx in range(304,579,21):bottle(xx,1518,SAGE)
    r(300,1557,283,3,PALE);end()
    furnishing('coldstock','stockrack',510,1615,85,162)
    g('restocker');person(418,1634,'restocker',SAGE);end()
    g('fan');box(318,1739,91,32,STEEL,DARK,10)
    p.append('<g transform="translate(363 1757)">');motion('fan-spin')
    path('M-3-3h6v-11h7v8h-7v9h11v7h-8v-7h-9v11h-7v-8h7v-9h-11v-7h8z',PALE);end();end();r(361,1755,5,5,INK);end()
    # Closed cleaning cupboard is separate from food equipment and WC basin.
    furnishing('cleaning','cleaning',40,1705,130,93)
    # Main rear area: receiving/storage and food preparation face a clear spine.
    r(32,1814,573,271,'#3d4b40')
    for xx in range(36,605,32):r(xx,1819,1,263,'#4a584a')
    wall(32,1809,170);wall(279,1809,327)
    # Delivery door is on the exterior wall, internal threshold shown only.
    g('delivery');r(21,1888,12,100,INK);r(32,1890,78,8,PALE);r(37,1892,65,3,WHITE);r(99,1898,5,5,MINT);end()
    furnishing('stock','stockrack',43,1831,132,163)
    g('receiving');box(177,1997,91,45,STEEL,DEEP,12);carton(185,2004,55,29)
    r(186,2060,9,7,INK);r(247,2060,9,7,INK)
    path('M254 1997v-27h9v34h-9z',PALE);end()
    furnishing('wash','sink',463,1834,134,131)
    g('foodprep');box(371,1988,226,47,PALE,STEEL,16)
    r(383,2000,72,27,SAGE);r(387,2003,63,21,PALE);r(390,2007,28,5,WHITE)
    r(465,1996,37,30,STEEL);r(469,2000,29,22,DARK)
    for xx in (472,479,486,493):r(xx,2002,2,18,PALE)
    path('M524 1997h21l4 4v17l-4 4h-21l-4-4v-17z',PALE);r(526,2002,17,14,DEEP);r(517,2007,4,8,STEEL);r(549,2007,4,8,STEEL)
    motion('prep-steam');path('M531 1993v-8h3v-5h-3v-7h3v-6h3v9h-3v5h3v12z',WHITE,'opacity=".6"');end()
    r(382,2045,7,7,INK);r(579,2045,7,7,INK);end()
    # A dedicated handwash basin (not the food wash-up sink).
    g('handsink');box(365,1848,72,41,STEEL,DARK,10);r(372,1856,56,25,PALE);r(380,1861,39,15,DEEP)
    path('M394 1861v-19h15v10h-4v-7h-7v16z',WHITE);r(424,1841,10,15,MINT);end()
    # Internal systems live ONLY in this office. Two screens, one work space.
    wall(32,2088,232);wall(354,2088,252)
    r(32,2100,573,233,'#2c3c33')
    for xx in range(37,601,24):r(xx,2104,1,222,'#34483a')
    furnishing('sys','sysdesk',42,2131,218,174)
    furnishing('cctv','cctvdesk',367,2131,218,174)
    # The handover board is on a short wall spur, shown by its top/page edges.
    # It must not become furniture blocking the central office passage.
    g('office');vwall(264,2100,102);r(275,2123,5,68,PALE)
    for yy in (2128,2146,2165):r(280,yy,3,15,WHITE)
    r(275,2191,7,3,STEEL);end()
    # Locker / rest room is behind another partition; the centre stays walkable.
    wall(32,2338,232);wall(354,2338,252)
    r(32,2350,573,282,'#334438')
    for xx in range(35,601,24):r(xx,2352,1,276,'#40503f')
    furnishing('breaktable','breaktable',45,2480,216,142)
    furnishing('lockers','lockers',451,2374,145,96)
    g('stafffridge');box(45,2371,69,50,PALE,STEEL,8)
    r(50,2375,59,39,WHITE);r(96,2421,9,3,INK)
    for xx in range(55,99,5):r(xx,2377,2,8,STEEL)
    end()
    g('kettle');box(145,2372,102,42,STEEL,DARK,8)
    path('M163 2377h22l5 5v16l-5 4h-22l-5-4v-16z',PALE)
    path('M166 2380h16l3 3v10l-3 3h-16l-3-3v-10z',STEEL)
    r(170,2383,8,6,WHITE);r(187,2384,7,12,INK);r(189,2387,3,6,PALE)
    path('M207 2382h14l3 3v13l-3 3h-14l-3-3v-13z',WHITE)
    r(208,2386,12,10,DEEP);r(224,2387,5,10,PALE)
    motion('break-steam');path('M214 2381v-7h3v-7h-3v-7h3v-5h3v8h-3v7h3v11z',WHITE,'opacity=".6"');end();end()
    g('bench');box(375,2522,57,77,SAGE,DEEP,11);r(381,2607,6,6,INK);r(419,2607,6,6,INK);end()
    g('clock');r(297,2379,38,24,INK);r(301,2382,30,16,PALE);r(313,2384,3,9,DEEP)
    p.append('<g transform="translate(316 2391)">');motion('clock-hand');r(0,-6,1,7,INK);end();end();end()
    wall(20,2637,600,15)
    p.append('</svg>')
    return ''.join(p)
