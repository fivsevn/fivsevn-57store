"""Original, layered pixel cutaway; 640 × 2660 integer authoring grid.

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
        p.append(f'<g transform="translate({x} {y}) scale({scale})">')
        r(3,0,6,3,WHITE);r(2,3,8,4,c);r(1,7,10,17,c);r(2,11,8,7,WHITE)
        r(4,12,5,4,DEEP);r(2,7,2,4,WHITE);r(2,22,8,2,STEEL);end()
    def pack(x,y,c=SAGE,kind='bag'):
        if kind=='bag':
            path(f'M{x+2} {y}h14v3h2v22h-18v-22h2z',INK)
            r(x+2,y+3,14,19,c);r(x+3,y+5,12,2,WHITE);r(x+5,y+10,9,8,WHITE);r(x+7,y+12,5,4,DEEP);r(x+3,y+21,12,2,STEEL)
            if (x+y)%3==0:
                r(x+3,y+9,12,2,DEEP);r(x+3,y+17,12,2,DEEP)
            elif (x+y)%3==1:
                path(f'M{x+5} {y+18}l4-9 5 9z',SAGE)
        elif kind=='box':
            r(x,y,18,24,INK);r(x+2,y+2,14,20,c);r(x+3,y+3,12,3,WHITE);r(x+4,y+9,9,8,DEEP);r(x+6,y+11,5,4,PALE)
            if x%3==0:
                r(x+4,y+8,4,10,WHITE);r(x+10,y+8,4,10,WHITE);r(x+5,y+7,2,2,INK);r(x+11,y+7,2,2,INK)
            elif x%3==1:
                r(x+3,y+8,12,11,PALE);r(x+6,y+10,6,2,WHITE)
        elif kind=='cup':
            path(f'M{x} {y+3}h19l-3 20h-13z',c);r(x,y,19,4,WHITE);r(x+4,y+8,11,7,DEEP);r(x+6,y+10,7,3,PALE);r(x+4,y+19,11,2,STEEL)
        elif kind=='bread':
            r(x,y+2,20,21,PALE);r(x+3,y+5,14,14,SAGE);r(x+5,y+4,10,3,WHITE);r(x+4,y+18,12,4,DEEP);r(x+3,y+1,14,2,STEEL)
            path(f'M{x+5} {y+14}v-5h3v-2h5v2h3v5z',WHITE);r(x+7,y+16,7,2,PALE)
    def carton(x,y,w=34,h=25):
        box(x,y,w,h,SAGE,DEEP,8);r(x+w//2-2,y+3,4,h-3,PALE);r(x+5,y+9,10,8,WHITE);r(x+7,y+11,6,2,STEEL)
    def person(x,y,kind,coat=PALE):
        p.append(f'<g transform="translate({x} {y})">');motion(kind)
        r(-6,32,37,8,INK,'opacity=".45"')
        g(cls='feet');r(2,28,8,12,INK);r(17,28,8,12,INK);end()
        r(0,12,27,20,coat);r(3,13,20,20,coat);r(8,12,7,17,DEEP)
        g(cls='hand');r(-5,15,6,15,coat);r(-5,27,6,5,PALE);end()
        r(27,17,6,12,coat);r(27,27,6,5,PALE)
        r(4,-1,19,17,PALE);r(1,-2,25,9,INK);r(4,-5,19,6,INK);r(2,5,5,9,INK)
        r(10,8,2,2,INK);r(19,8,2,2,INK)
        if kind in ('clerk','restocker'):r(17,17,6,3,WHITE)
        else:
            r(28,31,18,13,DEEP);r(28,31,18,3,MINT);r(31,27,12,2,PALE)
            for xx in (31,36,41):r(xx,36,2,5,SAGE)
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
    # Physical transom, resting on the window mullions, with readable branding.
    g('sign');box(25,20,590,77,DARK,STEEL,11)
    motion('sign-light');text(43,56,'57STORE',MINT,31);text(45,80,'ゴナナストア',PALE,14);end()
    r(253,33,2,49,STEEL)
    text(275,44,'每日生活、本地缓存。',WHITE,14)
    text(275,63,'Daily Life, Local Cache.',PALE,14)
    text(275,82,'暮らし、ローカルキャッシュ。',PALE,14);end()
    for xx,ww in ((32,211),(443,163)):
        r(xx,109,ww,29,INK);r(xx+4,112,ww-8,22,'#45695b');r(xx+5,114,ww-10,2,PALE)
        for k in range(xx+25,xx+ww-5,43):r(k,112,3,22,STEEL)
    g('door');r(246,107,194,42,INK);r(250,111,186,34,'#1b302a')
    for name,xx in [('door-left',250),('door-right',344)]:
        motion(name);r(xx,111,92,34,STEEL);r(xx+3,114,86,26,'#47675c');r(xx+3,115,85,2,PALE);r(xx+4,128,84,3,MINT);end()
    r(248,148,191,4,PALE);r(251,153,186,4,INK);r(334,108,14,4,MINT);end()
    g('mat');r(263,169,161,86,INK);r(268,174,151,76,'#234c3c')
    for yy in range(178,245,5):r(272,yy,143,1,'#35624d')
    r(276,181,135,3,SAGE);r(276,239,135,3,SAGE);end()
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
    for yy in (318,325,332):
        path(f'M435 {yy}h39l-4 24h-31z',STEEL);r(439,yy+3,31,3,PALE)
        for xx in (443,451,459):r(xx,yy+10,3,8,INK)
    end()
    g('umbrella');box(529,344,50,25,DEEP,STEEL,13)
    for xx,yy in ((536,324),(547,319),(562,328)):
        r(xx,yy,3,37,PALE);path(f'M{xx} {yy}v-8h9v7h-3v-4h-3v5z',MINT)
    end()
    device('coffee','coffee',39,424,118,159)
    g('bins')
    for xx in (43,95):
        box(xx,613,45,74,STEEL,DARK,13);r(xx+4,617,37,14,PALE);r(xx+11,622,23,5,INK)
        r(xx+8,651,29,20,SAGE);path(f'M{xx+14} 656h15v3h-15z',DARK)
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
    r(69,1380,7,7,DEEP);r(68,1389,9,13,DEEP);r(68,1402,3,10,DEEP);r(74,1402,3,10,DEEP)
    furnishing('toilet','toilet',40,1432,108,144)
    g('toiletbasin');box(127,1584,54,37,PALE,STEEL,10);r(134,1591,37,22,STEEL);r(140,1596,26,12,INK)
    path('M149 1593v-16h13v9h-3v-6h-7v13z',WHITE);r(172,1577,9,13,MINT)
    r(141,1544,37,26,STEEL);r(144,1547,31,20,'#aac1b5');path('M145 1548h6l22 18h-6z',WHITE,'opacity=".4"');end()
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
    r(521,1997,27,25,PALE);r(528,1992,13,4,STEEL)
    motion('prep-steam');path('M531 1993v-8h3v-5h-3v-7h3v-6h3v9h-3v5h3v12z',WHITE,'opacity=".6"');end()
    r(382,2045,7,21,INK);r(579,2045,7,21,INK);end()
    # A dedicated handwash basin (not the food wash-up sink).
    g('handsink');box(365,1848,72,41,STEEL,DARK,10);r(372,1856,56,25,PALE);r(380,1861,39,15,DEEP)
    path('M394 1861v-19h15v10h-4v-7h-7v16z',WHITE);r(424,1841,10,15,MINT);end()
    # Internal systems live ONLY in this office. Two screens, one work space.
    wall(32,2088,232);wall(354,2088,252)
    r(32,2100,573,233,'#2c3c33')
    for xx in range(37,601,24):r(xx,2104,1,222,'#34483a')
    furnishing('sys','sysdesk',42,2131,218,174)
    furnishing('cctv','cctvdesk',367,2131,218,174)
    g('office');r(278,2138,65,72,PALE);r(281,2141,59,66,STEEL)
    for xx,yy in ((286,2148),(313,2148),(292,2180)):
        r(xx,yy,22,24,WHITE);r(xx+3,yy+5,15,2,DEEP);r(xx+3,yy+10,13,2,DEEP)
    end()
    # Locker / rest room is behind another partition; the centre stays walkable.
    wall(32,2338,232);wall(354,2338,252)
    r(32,2350,573,282,'#334438')
    for xx in range(35,601,24):r(xx,2352,1,276,'#40503f')
    furnishing('breaktable','breaktable',45,2480,216,142)
    furnishing('lockers','lockers',451,2374,145,192)
    g('stafffridge');box(45,2371,69,50,PALE,STEEL,12);r(50,2381,58,30,SAGE);r(96,2388,4,13,INK);r(52,2417,51,3,STEEL);end()
    g('kettle');box(145,2380,102,30,STEEL,DARK,10);r(161,2358,27,33,PALE);r(165,2354,20,5,STEEL);r(189,2368,9,18,STEEL)
    r(207,2373,19,21,WHITE);r(226,2378,6,11,STEEL)
    motion('break-steam');path('M214 2371v-7h3v-7h-3v-7h3v-5h3v8h-3v7h3v11z',WHITE,'opacity=".6"');end();end()
    g('bench');box(375,2522,57,77,SAGE,DEEP,11);r(381,2607,6,15,INK);r(419,2607,6,15,INK);end()
    g('clock');r(297,2379,38,39,INK);r(301,2383,30,31,PALE);r(313,2387,3,15,DEEP)
    p.append('<g transform="translate(316 2400)">');motion('clock-hand');r(0,-11,1,13,INK);end();end();end()
    wall(20,2637,600,15)
    p.append('</svg>')
    return ''.join(p)
