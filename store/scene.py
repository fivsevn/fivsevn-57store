"""Original, layered pixel cutaway; 640 × 1500 integer authoring grid.

Customer circulation is open. Insulated rear room supplies the drink display;
only the enclosed rear rooms and the inside of the counter are staff space.
"""
from html import escape
import random
import re

INK='#101b1a'; DARK='#20312e'; STEEL='#647e74'; PALE='#bdcdc0'
WHITE='#e0e8d7'; MINT='#50efc2'; SAGE='#8ba78d'; DEEP='#304d40'
W,H=640,1500


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
    def shelf(ident,x,y,kind,height=238):
        g(ident);box(x,y,90,height,DARK,STEEL,14);r(x+42,y+8,6,height-10,PALE)
        g(cls='stock-response')
        for row,yy in enumerate(range(y+12,y+height-28,34)):
            for col,xx in enumerate((x+6,x+24,x+51,x+69)):
                c=[PALE,SAGE,'#588a75',WHITE][(row+col)%4]
                pack(xx,yy,c,kind)
            line(x+5,yy+26,35);line(x+50,yy+26,35)
        end();r(x+6,y+height-14,78,9,INK);end()
    def cabinet(ident,x,y,w,h,food):
        g(ident);box(x,y,w,h,DARK,STEEL,14)
        r(x+5,y+7,w-10,h-18,'#213d31')
        motion('case-light');r(x+6,y+9,w-12,4,MINT);r(x+7,y+13,w-14,h-25,MINT,'opacity=".035"');end()
        for row,yy in enumerate(range(y+22,y+h-20,35)):
            for col,xx in enumerate(range(x+9,x+w-15,24)):
                if food=='rice' and row%2==1:
                    path(f'M{xx} {yy+22}l20-22v22z',PALE);path(f'M{xx+4} {yy+20}l14-15v15z',WHITE);path(f'M{xx+8} {yy+18}l9-10v3l-6 7z',DEEP);r(xx+1,yy+23,20,2,STEEL)
                elif food=='rice':
                    path(f'M{xx} {yy+21}l9-20h4l9 20z',WHITE);r(xx+7,yy+12,8,10,DEEP);r(xx+1,yy+22,20,2,STEEL)
                elif food=='bento':
                    r(xx,yy+2,23,24,INK);r(xx+2,yy+4,19,19,PALE);r(xx+3,yy+5,9,15,WHITE)
                    r(xx+14,yy+5,6,7,SAGE);r(xx+14,yy+14,6,7,'#52745c');r(xx+2,yy+24,19,2,STEEL)
                elif row%2==0:
                    path(f'M{xx+2} {yy+3}l5-4h10l4 4v24h-19z',PALE);r(xx+4,yy+7,15,8,DEEP);r(xx+6,yy+10,11,2,WHITE);r(xx+4,yy+24,15,2,STEEL)
                else:pack(xx,yy,PALE,'cup')
            line(x+6,yy+27,w-12)
        # Low-opacity reflection belongs to the glass, not a screen overlay.
        motion('glass-light');path(f'M{x+8} {y+15}h9l{w-25} {h-36}h-9z',WHITE,'opacity=".065"');end();end()

    # Cutaway shell. Very restrained tile variation, not random pixel noise.
    r(8,18,624,1475,INK);r(18,25,604,1450,'#33433b')
    for yy in range(30,1470,32):
        for xx in range(22,620,32):r(xx,yy,31,31,rng.choice(['#34443c','#36463e','#35453d','#37473f']))
    r(20,30,8,1435,PALE);r(28,30,4,1435,STEEL);r(610,30,10,1435,PALE);r(606,30,4,1435,STEEL)
    # Public aisle light pools: broad hard-edged planes, no bloom filters.
    path('M248 220h206v820H248z',WHITE,'opacity=".025"')
    path('M32 370h110v645H32z',MINT,'opacity=".025"')

    # The frontage is at the TOP. Signs are physically on the glazing transom.
    g('sign');box(25,20,590,77,DARK,STEEL,11)
    motion('sign-light');text(43,56,'57STORE',MINT,31);text(45,80,'ゴナナストア',PALE,14);end()
    r(253,33,2,49,STEEL)
    text(275,44,'每日生活、本地缓存。',WHITE,12)
    text(275,63,'Daily Life, Local Cache.',PALE,12)
    text(275,82,'暮らし、ローカルキャッシュ。',PALE,12);end()
    # Glass frontage: magazine rack sits against the right-hand window.
    for xx,ww in ((32,211),(443,163)):
        r(xx,109,ww,29,INK);r(xx+4,112,ww-8,22,'#45695b');r(xx+5,114,ww-10,2,PALE)
        for k in range(xx+25,xx+ww-5,43):r(k,112,3,22,STEEL)
    g('door');r(246,107,194,42,INK);r(250,111,186,34,'#1b302a')
    for name,xx in [('door-left',250),('door-right',344)]:
        motion(name);r(xx,111,92,34,STEEL);r(xx+3,114,86,26,'#47675c');r(xx+3,115,85,2,PALE);r(xx+4,128,84,3,MINT);end()
    r(248,148,191,4,PALE);r(251,153,186,4,INK)
    r(334,108,14,4,MINT);end()
    # Mat is woven, unlettered, unmistakably a mat.
    g('mat');r(263,169,161,86,INK);r(268,174,151,76,'#234c3c')
    for yy in range(178,245,5):r(272,yy,143,1,'#35624d')
    r(276,181,135,3,SAGE);r(276,239,135,3,SAGE)
    r(282,186,3,48,STEEL);r(402,186,3,48,STEEL);end()

    # Cashier workspace, compact and bounded by the L counter. Entrance on right.
    r(36,151,187,141,'#27382f')
    g('warmers');box(41,162,81,62,STEEL,DARK,11);r(47,169,69,45,'#344d39')
    motion('warmer-light');r(48,170,67,4,WHITE);r(48,175,67,37,'#bbe4a4','opacity=".12"');end()
    for yy in (181,202):
        for xx in (52,73,94):
            path(f'M{xx} {yy}h12l3 4v8h-17v-8z',SAGE);r(xx+3,yy+2,7,3,PALE)
        line(48,yy+14,67)
    end()
    g('prep');box(137,161,74,49,PALE,STEEL,12);r(143,169,44,28,INK);r(148,173,34,20,DEEP)
    motion('microwave');text(191,180,'00',MINT,7);end();r(193,188,8,8,DARK)
    for xx in range(144,205,9):r(xx,215,5,3,INK)
    end()
    g('clerk');person(143,249,'clerk',MINT);end()
    g('receipt');box(39,291,184,49,PALE,STEEL,18);box(38,238,31,68,PALE,STEEL,12)
    r(43,337,175,4,MINT);r(48,346,165,6,DARK)
    box(100,278,58,30,INK,STEEL,8);r(106,282,46,19,DEEP)
    motion('pos-display');text(110,295,'¥ 057',MINT,10);end()
    r(107,313,42,5,INK);r(107,320,42,7,DEEP)
    box(167,295,41,24,STEEL,DARK,6);r(172,301,31,5,INK)
    g(cls='paper-response');motion('printer');r(176,304,24,31,WHITE)
    for yy in (310,315,320,325):r(180,yy,15 if yy!=325 else 9,1,STEEL)
    end();end()
    text(169,350,'RECEIPT',MINT,8);r(76,300,15,14,DEEP);r(79,303,9,4,PALE);end()
    # Window magazine display: angled covers, visible illustrations, price rails.
    g('magazines');box(500,156,97,146,DARK,STEEL,13)
    g(cls='stock-response')
    for row,yy in enumerate((165,208,251)):
        for col,xx in enumerate((509,536,563)):
            r(xx,yy,24,37,INK);r(xx+2,yy+2,20,33,[PALE,SAGE,'#47705c'][(row+col)%3]);r(xx+4,yy+4,16,4,WHITE)
            if col==0:
                path(f'M{xx+3} {yy+29}l8-17 10 17z',DEEP);r(xx+5,yy+30,14,2,WHITE)
            elif col==1:
                r(xx+9,yy+12,8,8,WHITE);r(xx+6,yy+20,12,10,DEEP)
            else:
                r(xx+5,yy+12,14,3,PALE);r(xx+5,yy+18,10,3,PALE);r(xx+5,yy+24,14,5,INK)
        line(505,yy+35,88)
    end();end()
    g('camera');r(565,111,4,24,STEEL);r(555,124,19,6,STEEL)
    motion('camera-swivel');path('M550 125h22v15h-22l-7-4v-7z',PALE);r(543,129,6,8,INK);r(552,127,6,2,WHITE);end();end()
    # Small arrival furniture occupies the entrance edge, not the door clearance.
    g('baskets')
    for yy in (279,286,293):
        path(f'M448 {yy}h37l-4 24h-29z',STEEL);r(452,yy+3,29,3,PALE)
        for xx in (456,464,472):r(xx,yy+10,3,8,INK)
    end()
    g('umbrella');box(529,324,50,25,DEEP,STEEL,13)
    for xx,yy in ((536,304),(547,299),(562,308)):
        r(xx,yy,3,37,PALE);path(f'M{xx} {yy}v-8h9v7h-3v-4h-3v5z',MINT)
    end()
    # Service appliances each retain their own recognisable silhouette.
    g('coffee');box(40,391,85,67,STEEL,DARK,12);box(47,370,65,66,DARK,STEEL,12)
    r(54,376,50,19,INK);r(58,381,42,7,MINT);r(57,401,43,26,INK)
    r(71,405,16,16,WHITE);r(87,409,5,8,PALE);r(63,430,36,3,PALE)
    motion('steam');path('M75 402v-5h3v-6h-3v-6h3v-5h3v8h-3v6h3v8z',WHITE,'opacity=".65"');end()
    r(94,447,17,4,MINT);end()
    g('bins')
    for xx in (43,86):
        box(xx,493,37,63,STEEL,DARK,13);r(xx+4,497,29,14,PALE);r(xx+10,502,17,5,INK);r(xx+7,526,23,17,SAGE)
        path(f'M{xx+12} 532h13v3h-13z',DARK)
    end()
    g('sys');box(515,389,79,101,STEEL,DARK,14);box(521,367,67,54,INK,STEEL,11)
    r(527,374,55,37,'#124f3d')
    g(cls='screen-response');text(538,391,'SYS',MINT,13)
    motion('terminal-type');r(533,398,35,2,MINT);r(533,404,24,2,MINT);end();end()
    r(524,435,61,18,PALE)
    for yy in (438,443,448):
        for xx in range(527,582,7):r(xx,yy,4,2,DARK)
    r(534,465,44,6,INK);r(542,470,28,16,PALE);end()

    # Four distinct central gondolas; cross aisle and side aisles stay open.
    shelf('snacks',192,427,'bag',226)
    shelf('noodles',360,427,'cup',226)
    shelf('bread',192,754,'bread',190)
    shelf('daily',360,754,'box',190)
    # End cap facings are part of their gondola's inspection area.
    for xx,yy in ((198,653),(366,653),(198,944),(366,944)):
        box(xx,yy,78,25,STEEL,DARK,9)
        for bx in range(xx+5,xx+68,21):pack(bx,yy+1,SAGE,'box')

    cabinet('fresh',519,558,77,181,'rice')
    cabinet('bento',519,791,77,174,'bento')
    cabinet('dairy',42,618,80,138,'dairy')
    # Sliding glass chest freezer, distinct from the walk-in drink wall.
    g('freezer');box(43,805,80,158,PALE,STEEL,16);r(48,813,70,143,DEEP)
    for yy in (821,867,913):
        for xx in (54,84):
            r(xx,yy,25,33,PALE);r(xx+4,yy+7,17,16,SAGE);r(xx+7,yy+11,11,9,WHITE)
    motion('freezer-light');r(49,814,3,140,MINT);end()
    r(49,879,68,4,STEEL);r(54,875,25,3,WHITE);r(87,885,25,3,WHITE)
    motion('freezer-reflection');path('M55 817h8l47 131h-8z',WHITE,'opacity=".18"');end();end()

    # A customer walks along the central aisle, with separately stepped feet.
    g('shopper');person(312,578,'shopper',PALE);end()
    g('reader');person(466,181,'reader',SAGE);end()
    # Rail-ended promotional basket: low, doesn't close the cross aisle.
    g('special');p.append('<g transform="translate(-325 -6)">');box(365,1011,86,41,STEEL,DARK,12)
    for yy in (1016,1033):
        for xx in (372,397,422):pack(xx,yy,PALE,'bread')
    r(370,1050,76,5,PALE);end();end()
    # Behind the drink doors is a real, deep insulated room, shown as a cutaway.
    r(270,1158,334,300,'#243c34')
    for yy in range(1162,1455,24):r(274,yy,325,1,'#355247')
    r(31,1160,226,298,'#28382f')
    for xx in range(35,250,26):r(xx,1164,1,286,'#32473a')
    wall(30,1149,81);wall(203,1149,59)
    # Actual staff door / door leaf, with hinge and small glazed window.
    g('staffdoor');r(112,1152,89,8,INK);path('M112 1160v76h8v-76z',PALE);r(114,1166,3,27,DEEP);r(119,1213,4,4,MINT);end()
    # Front of walk-in display. The reverse rack is visible INSIDE the room.
    g('drinks');box(280,1012,318,121,DARK,STEEL,17)
    for col,xx in enumerate((287,389,491)):
        r(xx,1019,98,105,STEEL);r(xx+4,1023,90,96,'#203b30')
        motion('drinks-light');r(xx+5,1025,3,91,MINT);r(xx+9,1025,80,91,MINT,'opacity=".035"');end()
        for row,yy in enumerate((1029,1068)):
            for i in range(6):bottle(xx+12+i*13,yy,[MINT,PALE,SAGE][(i+col+row)%3])
            line(xx+10,yy+28,79)
        r(xx+87,1061,3,23,PALE)
        motion('drink-reflection');path(f'M{xx+13} 1026h7l65 89h-7z',WHITE,'opacity=".11"');end()
    r(291,1137,64,3,MINT);r(402,1137,24,3,PALE);r(505,1137,31,3,MINT);end()
    # Insulated divider, opening is a thick swing door from the back room.
    wall(258,1160,12,100);wall(258,1352,12,109)
    g('colddoor');r(258,1260,13,92,INK);r(270,1262,66,10,PALE);r(274,1264,55,3,WHITE);r(320,1270,8,4,STEEL);end()
    # Reverse shelves have bottle backs, cases, hand truck and a clear aisle.
    g('walkin');box(286,1176,303,44,STEEL,DEEP,14)
    for xx in range(295,577,21):bottle(xx,1182,SAGE)
    for yy in (1323,1370,1417):
        box(546,yy,48,32,STEEL,DEEP,10)
        for xx in (551,574):bottle(xx,yy+2,PALE,.75)
    carton(295,1383,45,32);carton(342,1400,42,31);carton(292,1416,45,28)
    r(382,1396,40,4,STEEL);r(383,1400,4,29,STEEL);r(416,1400,4,29,STEEL);r(381,1427,42,6,PALE);r(383,1433,7,6,INK);r(413,1433,7,6,INK)
    end()
    g('restocker');person(430,1267,'restocker',SAGE);end()
    g('fan');box(421,1421,88,32,STEEL,DARK,8)
    p.append('<g transform="translate(465 1438)">');motion('fan-spin')
    path('M-3-3h6v-11h7v8h-7v9h11v7h-8v-7h-9v11h-7v-8h7v-9h-11v-7h8z',PALE);end();end()
    r(463,1436,5,5,INK);end()
    # Back stock / staff utilities. Door connects directly to a public aisle.
    g('stock');box(38,1175,62,73,STEEL,DARK,9)
    for xx,yy in ((43,1180),(43,1213)):carton(xx,yy,45,22)
    carton(137,1221,42,26);carton(181,1211,34,24);end()
    g('lockers')
    for xx in (177,210):
        box(xx,1175,29,63,STEEL,DARK,7);r(xx+19,1201,3,8,INK)
        for yy in (1182,1186,1190):r(xx+5,yy,18,2,INK)
    end()
    g('sink');box(40,1271,58,36,STEEL,DARK,10);r(46,1277,43,23,INK);r(51,1280,33,16,PALE)
    path('M62 1278v-15h13v10h-4v-6h-5v11z',WHITE);r(86,1265,9,14,MINT);end()
    # A short office partition with a real opening, not an imaginary floor label.
    wall(31,1323,108,8);wall(224,1323,31,8)
    g('office');box(40,1344,202,59,STEEL,DARK,14)
    r(47,1413,7,25,INK);r(228,1413,7,25,INK)
    box(174,1360,49,30,PALE,STEEL,5)
    for yy in (1367,1373,1379):r(179,yy,33,2,STEEL)
    r(226,1351,10,17,WHITE);r(236,1355,5,9,STEEL)
    box(97,1427,41,24,DARK,INK,5);r(114,1451,6,10,STEEL)
    end()
    g('cctv');box(63,1340,86,46,INK,STEEL,9);r(69,1346,74,33,DEEP)
    for xx,yy in ((73,1350),(108,1350),(73,1365),(108,1365)):
        r(xx,yy,30,11,'#6c9780');r(xx+3,yy+3,8,6,DEEP);r(xx+17,yy+3,10,2,PALE)
    g(cls='screen-response');motion('cctv-scan');r(72,1351,68,2,MINT,'opacity=".6"');end();end()
    r(99,1386,14,6,STEEL);r(88,1390,36,4,INK);r(66,1399,78,8,PALE)
    for xx in range(70,140,8):r(xx,1401,4,3,STEEL)
    text(113,1385,'CCTV',MINT,6);end()
    # Small wall clock above the desk, animated hand rather than extra interface.
    g('clock');r(222,1273,26,30,INK);r(225,1276,20,24,PALE);r(232,1280,4,11,DEEP)
    p.append('<g transform="translate(235 1289)">');motion('clock-hand');r(0,-8,1,10,INK);end();end();end()
    wall(20,1467,600,15)
    p.append('</svg>')
    return ''.join(p)
