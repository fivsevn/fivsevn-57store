"""Original pixel cutaway. Integer-coordinate SVG, deterministic and dependency-free.

640 x 1040 world coordinates; no external art, raster payload or runtime renderer.
The central/public aisles and the left staff passage are intentionally kept clear.
"""
from html import escape
import random
import re

INK = '#101a1a'
DARK = '#1b2928'
STEEL = '#6d8280'
PALE = '#c9d9d3'
WHITE = '#e5eee4'
MINT = '#50efc2'


def render_entries(config):
    expected = {'receipt': '/receipt/', 'sys': '/sys/', 'cctv': '/cctv/'}
    entries = config['entries']
    if len(entries) != 3 or {e['id']: e['href'] for e in entries} != expected:
        raise ValueError('The store opens exactly receipt, sys and cctv')
    return '\n'.join(
        f'<a class="store-entry entry-{e["id"]}" data-store-object="{e["id"]}" href="{e["href"]}">'
        f'<span class="store-visually-hidden">{escape(e["label"])} / {escape(e["subtitle"])}</span></a>'
        for e in entries
    )


def render_labels(config):
    """Shelf labels are authored content, not a network inventory feed."""
    result=[]
    ids=set()
    for fixture in config['fixtures']:
        ident=fixture['id']
        if not re.fullmatch('[a-z]+',ident) or ident in ids:
            raise ValueError('Invalid or duplicate store fixture')
        ids.add(ident)
        name=escape(fixture['name'])
        result.append(f'<button type="button" hidden class="store-object object-{ident}" data-store-object="{ident}" aria-haspopup="dialog" aria-controls="label-{ident}"><span class="store-visually-hidden">查看{name}</span></button>')
        rows=''.join(f'<li>{escape(item)}</li>' for item in fixture['items'])
        result.append(f'<dialog class="shelf-label" id="label-{ident}" aria-labelledby="title-{ident}">'
                      f'<div class="label-code"><span>57STORE / {escape(fixture["code"])}</span><form method="dialog"><button aria-label="收起{name}标签" autofocus>×</button></form></div>'
                      f'<h2 id="title-{ident}">{name}</h2><p class="label-subtitle">{escape(fixture["subtitle"])}</p>'
                      f'<ul>{rows}</ul><p class="label-note">{escape(fixture["note"])}</p>'
                      '<div class="label-barcode" aria-hidden="true"></div></dialog>')
    return ''.join(result)


def render_scene():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" class="store-art" viewBox="26 26 586 924" width="586" height="924" aria-hidden="true" focusable="false" shape-rendering="crispEdges">']
    rng = random.Random(57)

    def rect(x, y, w, h, color, extra=''):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" {extra}/>')

    def path(d, color, extra=''):
        parts.append(f'<path d="{d}" fill="{color}" {extra}/>')

    def label(x, y, text, color=PALE, size=8, anchor='start'):
        parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}" letter-spacing="1" text-anchor="{anchor}" shape-rendering="auto">{escape(text)}</text>')

    def box(x, y, w, h, top=PALE, face=STEEL, depth=12):
        rect(x+7, y+depth+5, w, h, '#101918', 'opacity=".55"')
        rect(x, y, w, h+depth, INK)
        rect(x+2, y+2, w-4, h-2, top)
        rect(x+2, y+h, w-4, depth-2, face)
        rect(x+3, y+3, w-6, 2, WHITE)
        rect(x+w-4, y+5, 2, h-5, STEEL)

    def bottle(x, y, color=MINT, size=1):
        parts.append(f'<g transform="translate({x} {y}) scale({size})">')
        rect(2,0,4,3,PALE);rect(1,3,6,3,color);rect(0,6,8,13,color)
        rect(1,9,6,5,WHITE);rect(2,10,4,3,STEEL);rect(1,6,1,3,WHITE)
        rect(1,18,6,2,'#2a7362');parts.append('</g>')

    def packet(x, y, color=PALE, w=10, h=15):
        rect(x,y,w,h,INK);rect(x+1,y+1,w-2,h-2,color)
        rect(x+2,y+2,w-4,2,WHITE);rect(x+2,y+6,w-4,4,DARK)
        rect(x+2,y+h-3,w-4,1,STEEL)

    def carton(x,y,w=30,h=24):
        box(x,y,w,h,'#788c7c','#43564c',7)
        rect(x+w//2-2,y+2,4,h-2,'#b4c2a5')
        rect(x+5,y+8,9,6,PALE);rect(x+6,y+9,6,1,DARK)
        rect(x+5,y+h+2,8,2,INK)

    def person(x,y,coat=PALE,kind='shopper'):
        parts.append(f'<g transform="translate({x} {y})"><g class="{kind}">')
        rect(-5,24,28,7,INK,'opacity=".5"')
        rect(1,21,6,10,INK);rect(12,21,6,10,INK)
        rect(-1,8,20,17,coat);rect(2,11,13,11,coat)
        rect(-4,11,5,10,coat);rect(19,10,4,11,coat)
        rect(-4,20,5,4,PALE);rect(19,20,4,4,PALE)
        rect(2,-2,14,14,'#90aaa0');rect(0,-3,17,7,INK)
        rect(1,-5,14,5,INK);rect(0,2,4,7,INK)
        rect(5,5,2,2,INK);rect(12,5,2,2,INK)
        if kind=='clerk':
            rect(2,13,14,4,WHITE);rect(12,13,3,2,DARK)
        else:
            rect(19,21,13,12,'#709985');rect(21,18,9,2,PALE)
            rect(20,23,11,2,MINT)
        parts.append('</g></g>')

    # Building footprint, cutaway foundation and tile floor.
    rect(28,47,594,925,'#030b0b','opacity=".7"')
    rect(28,28,584,926,INK)
    rect(36,38,568,906,'#354340')
    for y in range(46,936,28):
        for x in range(42,596,28):
            color=rng.choice(['#2b3734','#2d3936','#303c38','#2e3a37'])
            rect(x,y,27,27,color)
            if rng.random()<.22:rect(x+17,y+19,2,1,'#45504a')
    # Light falls across the public aisles without filters or blur.
    rect(147,284,352,413,'#c5efda','opacity=".035"')
    rect(287,286,57,562,'#b8edd5','opacity=".04"')
    # Rear service area: replenishment room, sink, lockers and office desk.
    rect(44,45,548,120,'#202d2b')
    for x in range(45,590,20):rect(x,45,1,118,'#283936')
    box(50,48,208,23,'#52615c','#293a35',8)
    for x,y in [(57,54),(93,55),(131,52),(170,54),(205,56),(65,108),(101,112)]:carton(x,y,28,22)
    label(183,144,'STOCK / 57',STEEL,8,'middle')
    box(295,53,49,30,STEEL,DARK)
    rect(301,58,35,20,INK);rect(306,61,25,13,'#8faaa1')
    path('M315 58v-9h10v8h-3v-5h-4v6',WHITE)
    # Employee lockers.
    for x in (364,389,414):
        box(x,52,23,61,'#758c81','#43564e',8)
        rect(x+3,56,16,2,PALE);rect(x+15,80,2,7,INK)
        for y in (59,62,65):rect(x+4,y,13,1,DARK)
    rect(451,47,7,117,STEEL);rect(453,47,3,117,PALE)
    box(475,59,97,31,STEEL,DARK)
    box(496,61,32,19,INK,STEEL,5);rect(500,64,24,12,'#345b4e')
    rect(503,67,16,2,MINT);rect(534,63,21,20,PALE)
    for yy in (67,71,75):rect(536,yy,14,1,STEEL)
    box(508,112,28,21,DARK,INK,5);rect(519,133,6,8,STEEL)
    label(523,155,'OFFICE',STEEL,7,'middle')
    # Back wall and service doorway. Door opens into the stock room.
    box(40,166,35,10,PALE,STEEL,14)
    box(132,166,463,10,PALE,STEEL,14)
    rect(78,168,52,6,MINT);rect(80,136,4,31,STEEL)
    label(103,202,'STAFF',STEEL,7,'middle')
    parts.append('<g id="fixture-drinks">')
    # Walk-in coolers: rear replenishment, five glass doors facing the store.
    box(164,191,408,64,STEEL,DARK,24)
    rect(167,193,402,13,INK);label(369,203,'COLD DRINKS   /   冷蔵',MINT,8,'middle')
    for index in range(5):
        x=170+index*79
        rect(x,209,73,65,INK);rect(x+3,211,67,59,'#1e3d34')
        for yy in (215,243):
            for j in range(6):bottle(x+7+j*10,yy,MINT if (j+index)%3 else '#b7d4be',.8)
        rect(x+3,238,67,3,STEEL);rect(x+3,265,67,3,STEEL)
        rect(x+3,211,2,54,WHITE);rect(x+69,211,2,58,PALE)
        rect(x+60,233,3,13,PALE)
        path(f'M{x+8} 212h12l36 55h-9z',WHITE,'opacity=".07"')
        rect(x+11,271,15,2,MINT);rect(x+35,271,16,2,STEEL)
    parts.append('</g>')
    # Staff passage: clear from rear stock room to behind the counter.
    rect(129,232,6,427,INK);rect(130,232,3,427,STEEL)
    for y in (326,468,604):
        label(100,y,'·',STEEL,12)
    box(49,318,29,49,STEEL,DARK)
    for y in range(322,360,6):rect(53,y,20,2,INK)
    label(85,419,'STAFF',STEEL,7,'middle')
    label(85,431,'ONLY',STEEL,7,'middle')
    carton(51,516,28,29);carton(51,555,25,22)
    # Utility cart parked in its bay, away from the service lane.
    box(48,620,29,37,STEEL,DARK,8)
    for yy in (628,641):rect(51,yy,21,2,PALE)
    rect(50,662,5,5,INK);rect(70,662,5,5,INK)
    # Floor aisle markings and a loose end-cap basket.
    label(170,323,'01',STEEL,9)
    label(348,323,'02',STEEL,9)
    label(515,323,'03',STEEL,9)

    def gondola(x,y,title,variant):
        parts.append(f'<g id="fixture-{"snacks" if variant==0 else "daily"}">')
        box(x,y,82,238,'#88988b','#4c6157',17)
        rect(x+4,y+5,74,222,DARK)
        # Central spine and double-sided stock, seen over their shoulders.
        rect(x+38,y+7,6,217,PALE);rect(x+40,y+7,2,217,WHITE)
        parts.append('<g class="stock-response">')
        for row in range(7):
            yy=y+11+row*29
            for col in range(2):
                for side in (0,1):
                    xx=x+8+side*40+col*13
                    shade=[PALE,'#85baa2','#c4cfb3','#527769'][((row*3+col+side+variant)%4)]
                    if variant==1 and row%3==0:bottle(xx,yy,shade)
                    else:packet(xx,yy,shade,11,21 if row%2 else 17)
            rect(x+5,yy+24,31,3,STEEL);rect(x+46,yy+24,30,3,STEEL)
            for offset in (9,23,50,65):rect(x+offset,yy+24,7,2,WHITE)
        parts.append('</g>')
        rect(x+5,y+230,72,20,INK)
        label(x+41,y+242,title,MINT,8,'middle')
        rect(x+9,y+251,64,2,PALE)
        for xx in (x+7,x+69):rect(xx,y+255,6,5,INK)
        parts.append('</g>')
    gondola(200,362,'SNACKS',0)
    gondola(365,362,'DAILY',1)
    # Short endcap on the back of the left shelf.
    box(207,344,68,15,STEEL,DARK,5)
    for x in range(213,267,13):packet(x,344,PALE,10,12)
    parts.append('<g id="fixture-fresh">')
    # Wall-side fresh food case. Angled glass lip and three stocked levels.
    box(518,357,66,281,STEEL,DARK,21)
    rect(522,362,58,265,INK)
    label(552,374,'FRESH',MINT,7,'middle')
    for row in range(8):
        yy=385+row*29
        for col in range(3):
            xx=526+col*17
            if row<3:
                path(f'M{xx} {yy+13}l6-12h3l6 12v4h-15z',WHITE)
                rect(xx+5,yy+10,6,7,'#305347')
            else:
                packet(xx,yy,PALE if row%2 else '#91ad98',14,19)
                rect(xx+2,yy+9,10,5,'#578775')
        rect(524,yy+22,53,3,STEEL);rect(529,yy+22,10,2,WHITE)
    rect(522,380,2,245,MINT,'opacity=".6"')
    path('M526 381h9l36 59v36z',WHITE,'opacity=".06"')
    parts.append('</g>')
    # Wall screen and camera.
    parts.append('<g id="fixture-cctv">')
    box(506,286,78,54,STEEL,INK,6)
    rect(510,290,70,40,INK)
    parts.append('<g class="screen-response">')
    for xx,yy in ((513,293),(547,293),(513,311),(547,311)):
        rect(xx,yy,29,15,'#355c4d');rect(xx+3,yy+3,7,8,'#88bd9f')
        rect(xx+13,yy+5,12,3,'#628e79')
    parts.append('</g>')
    label(545,340,'CCTV',MINT,10,'middle')
    rect(576,334,3,3,MINT,'class="status-light"')
    rect(590,273,8,5,STEEL)
    path('M567 266h23v16h-7v-3h-16z',PALE)
    rect(566,268,8,9,INK);rect(566,271,4,3,MINT)
    parts.append('</g>')
    # Two shoppers, kept in passable aisles.
    person(313,494,'#8e9c90')
    person(478,397,'#4d7768','still-shopper')
    # Front cross-aisle: baskets and promotion island, leaving a broad entrance path.
    parts.append('<g id="fixture-arrival">')
    box(381,694,68,45,STEEL,DARK,13)
    for xx in (387,404,421):
        for yy in (699,717):packet(xx,yy,'#acc5ad',14,14)
    rect(384,741,62,7,INK);label(416,747,'NEW ARRIVAL',MINT,5,'middle')
    parts.append('</g>')
    # Back counter appliances,
    parts.append('<g id="fixture-coffee">')
    box(61,682,217,29,STEEL,DARK,14)
    box(66,668,35,35,PALE,STEEL,8)
    rect(71,673,25,17,INK);rect(74,678,19,2,MINT)
    rect(77,693,13,7,INK);label(84,721,'COFFEE',PALE,5,'middle')
    box(107,680,43,24,PALE,DARK,8)
    rect(111,684,30,14,INK);rect(114,686,24,10,'#5a7466');rect(143,685,3,3,MINT)
    for xx in range(158,272,13):packet(xx,687,PALE,10,15)
    parts.append('</g>')
    person(176,733,MINT,'clerk')
    box(62,773,218,49,'#a5b6ab','#60786b',25)
    rect(65,823,212,3,MINT)
    for xx in (68,137,206):
        rect(xx,829,65,13,DARK);rect(xx+3,832,59,1,STEEL)
    # Glass hot-food cabinet with tiny trays.
    box(70,745,54,44,PALE,DARK,9)
    rect(74,750,46,32,'#294036')
    for yy in (755,770):
        for xx in (78,91,104):
            rect(xx,yy,9,7,'#bfc7a6');rect(xx+2,yy+1,6,3,WHITE)
        rect(76,yy+8,42,2,STEEL)
    rect(75,751,2,28,WHITE)
    # POS and paper printer.
    box(158,757,40,22,STEEL,DARK,5)
    rect(161,759,33,16,INK);rect(165,762,25,3,MINT)
    for xx in range(166,192,5):rect(xx,768,3,3,PALE)
    rect(175,781,9,8,DARK);box(160,789,38,9,PALE,STEEL,3)
    parts.append('<g id="fixture-receipt">')
    box(217,780,33,22,PALE,DARK,7);rect(221,785,24,5,INK)
    parts.append('<g class="paper-response">')
    rect(223,789,20,25,WHITE)
    for yy in range(793,812,4):rect(226,yy,14 if yy%3 else 9,1,STEEL)
    parts.append('</g></g>')
    label(101,859,'COUNTER / レジ',PALE,8)
    rect(212,829,57,14,INK)
    label(240,840,'RECEIPT',MINT,9,'middle')
    # Queue starts after the entry and stays off the central through aisle.
    for yy in (868,884):rect(214,yy,42,2,'#6f8c77')
    path('M230 873h10l-5-6z','#8fb39b')
    # Customer terminal / copy station on the front right.
    parts.append('<g id="fixture-sys">')
    box(517,755,61,58,STEEL,DARK,17)
    box(524,724,46,37,PALE,STEEL,8)
    rect(528,728,38,27,INK);rect(531,731,32,21,'#224b3c')
    parts.append('<g class="screen-response">')
    label(547,740,'SYS',MINT,9,'middle')
    rect(535,745,21,2,MINT);rect(535,750,11,1,PALE)
    parts.append('</g>')
    rect(523,778,45,10,PALE)
    for xx in range(526,566,6):
        for yy in (780,784):rect(xx,yy,4,2,DARK)
    rect(526,803,36,3,INK);rect(531,806,28,13,WHITE)
    parts.append('</g>')
    # Green baskets and umbrella rack by the front glazing.
    for yy in (875,882,889):
        box(485,yy,33,13,'#467c64',DARK,3)
        for xx in range(489,513,6):rect(xx,yy+4,3,6,INK)
    box(552,870,29,40,STEEL,INK,5)
    for xx,yy in ((558,850),(566,846),(574,854)):
        rect(xx,yy,2,45,PALE);path(f'M{xx} {yy}v-6h6v6h-2v-4h-2v4',MINT)
    # Shop-front windows and open sliding entrance, no queue crossing the doors.
    box(40,921,264,8,PALE,STEEL,18)
    box(448,921,149,8,PALE,STEEL,18)
    for x,w in ((49,246),(457,131)):
        rect(x,884,w,36,'#182b27','opacity=".72"')
        rect(x,884,w,3,PALE);rect(x,917,w,3,STEEL)
        for xx in range(x,x+w,43):rect(xx,884,3,36,STEEL)
        rect(x,903,w,3,MINT,'opacity=".65"')
    label(176,899,'57STORE ゴナナストア',MINT,11,'middle')
    # Door frame and sliding panels retract into the sides.
    rect(299,883,6,65,PALE);rect(443,883,6,65,PALE)
    rect(305,883,138,6,STEEL);rect(308,884,132,2,MINT)
    for x in (307,421):
        rect(x,891,20,47,'#25443a');rect(x,891,2,47,PALE)
        rect(x,912,20,3,MINT)
    rect(330,897,88,33,'#3b5545')
    for xx in range(332,417,4):rect(xx,900,1,27,'#536c57')
    label(374,917,'57',MINT,13,'middle')
    rect(306,941,136,5,STEEL)
    # Cutaway perimeter: solid wall caps and metal corner protectors.
    rect(31,29,578,8,WHITE);rect(37,37,566,6,STEEL)
    rect(31,37,10,905,PALE);rect(41,43,4,878,STEEL)
    rect(596,37,12,907,PALE);rect(593,43,3,878,STEEL)
    for x,y in ((32,30),(597,30),(32,931),(597,931)):
        rect(x,y,9,9,INK);rect(x+2,y+2,5,5,STEEL)
    # Fluorescent bars and wiring against the cutaway walls.
    for x in (160,334,508):
        rect(x,29,60,8,INK);rect(x+4,31,52,3,MINT)
    for y in (318,540,760):
        rect(30,y,7,44,INK);rect(32,y+3,3,38,WHITE)
        rect(602,y,7,44,INK);rect(604,y+3,3,38,WHITE)
    parts.append('</svg>')
    return ''.join(parts)
