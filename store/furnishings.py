"""Original high-angle shop furnishings, made entirely from SVG geometry.

One projection throughout: X is horizontal, floor Y runs down the screen, and
height only lifts an object upward. Broad plan surfaces dominate. The south
edge shows a short amount of thickness; there are no isometric side planes.
"""
from math import isfinite

INK='#101b1a'; SHADOW='#182620'; DARK='#283d33'; DEEP='#3e5b48'
STEEL='#6b8174'; SAGE='#91a58b'; PALE='#c4d0bb'; WHITE='#e7ecdc'; MINT='#50efc2'


class _Drawing:
    def __init__(self): self.parts=[]
    def rect(self,x,y,w,h,fill,attrs=''):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {attrs}/>')
    def path(self,d,fill,attrs=''):
        self.parts.append(f'<path d="{d}" fill="{fill}" {attrs}/>')
    def polygon(self,points,fill,attrs=''):
        self.parts.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill}" {attrs}/>')
    def start(self,attrs=''): self.parts.append(f'<g {attrs}>')
    def end(self): self.parts.append('</g>')
    def oval(self,x,y,w,h,fill):
        a=max(2,w//5);b=max(2,h//4)
        self.polygon([(x+a,y),(x+w-a,y),(x+w,y+b),(x+w,y+h-b),
                      (x+w-a,y+h),(x+a,y+h),(x,y+h-b),(x,y+b)],fill)
    def shadow(self,x,y,w,h): self.oval(x+3,y+5,w,h,INK)
    def slab(self,x,y,w,h,lip=8,top=PALE,front=STEEL):
        """A broad top and a short south-facing edge, never a standing facade."""
        self.rect(x+4,y+6,w,h,INK,'opacity=".35"')
        self.rect(x,y,w,h,INK)
        self.rect(x+2,y+2,w-4,h-lip-2,top)
        self.rect(x+2,y+h-lip,w-4,lip-2,front)
        self.rect(x+3,y+3,w-6,2,WHITE)
        self.rect(x+3,y+h-lip,w-6,2,PALE)
    def rail(self,x,y,w):
        self.rect(x,y,w,4,STEEL);self.rect(x,y,w,1,PALE)
        for xx in range(x+4,x+w-10,23):
            self.rect(xx,y+1,13,2,WHITE);self.rect(xx+2,y+2,4,1,DEEP)


def _bag_top(d,x,y,v):
    c=(SAGE,PALE,DEEP,STEEL)[v%4]
    # Full pillow-shaped pack seen from above, crimped ends and inflated centre.
    d.path(f'M{x+2} {y}h15v3h2v3h1v10h-1v3h-2v3H{x+2}v-3H{x}v-3h-1V{y+6}h1V{y+3}h2z',INK)
    d.path(f'M{x+3} {y+3}h12l3 4v8l-3 4H{x+3}l-2-4V{y+7}z',c)
    d.rect(x+2,y+1,15,3,PALE);d.rect(x+2,y+19,15,3,STEEL)
    for xx in range(x+3,x+17,3):d.rect(xx,y,1,3,WHITE);d.rect(xx,y+20,1,2,INK)
    d.rect(x+4,y+5,10,2,WHITE)
    if v%3==0:
        d.oval(x+5,y+9,9,7,PALE);d.rect(x+7,y+10,4,2,WHITE);d.rect(x+8,y+14,4,1,STEEL)
    elif v%3==1:
        d.oval(x+4,y+9,10,7,DEEP);d.rect(x+6,y+10,2,2,PALE);d.rect(x+10,y+13,2,2,PALE)
    else:
        for xx in (x+5,x+10):
            d.rect(xx,y+9,4,7,DEEP);d.rect(xx+1,y+10,2,2,PALE)
    d.rect(x+2,y+8,2,8,WHITE,'opacity=".45"')


def _cup_top(d,x,y,v):
    # The lid occupies almost the whole silhouette; the cup wall is only 3px.
    d.oval(x,y+3,20,19,INK);d.oval(x+1,y+5,18,17,SAGE if v%2 else STEEL)
    d.oval(x,y,20,18,WHITE);d.oval(x+2,y+2,16,13,PALE if v%2 else SAGE)
    d.rect(x+5,y+4,10,2,DEEP);d.rect(x+6,y+8,8,4,DEEP)
    d.rect(x+8,y+9,4,1,WHITE);d.rect(x+16,y+1,5,3,WHITE)
    d.rect(x+4,y+15,12,1,STEEL);d.rect(x+4,y+20,12,1,PALE)


def _bread_top(d,x,y,v):
    d.path(f'M{x+2} {y}h16v3h2v17h-2v3H{x+2}v-3H{x}V{y+3}h2z',STEEL)
    d.rect(x+2,y+2,16,19,PALE)
    if v%3==0:
        # Sliced square loaf: a crust around a light face and layered edges.
        d.path(f'M{x+4} {y+17}V{y+6}h2V{y+4}h8v2h2v11z',SAGE)
        d.path(f'M{x+6} {y+15}V{y+7}h8v8z',WHITE)
        d.rect(x+4,y+18,12,1,DEEP);d.rect(x+5,y+20,10,1,SAGE)
    elif v%3==1:
        # Round bun, with a scored crown rather than a rectangular bread icon.
        d.oval(x+3,y+5,14,13,SAGE);d.oval(x+5,y+7,10,8,WHITE)
        d.rect(x+9,y+6,2,11,SAGE);d.rect(x+4,y+11,12,2,SAGE)
    else:
        # Curved croissant: tapered tips and three distinct folded segments.
        d.path(f'M{x+2} {y+8}h3V{y+5}h10v3h3v7h-4v-3h-2v-2H{x+8}v2H{x+6}v3H{x+2}z',SAGE)
        d.rect(x+7,y+5,3,5,WHITE);d.rect(x+11,y+6,3,5,PALE)
        d.rect(x+4,y+8,2,5,PALE);d.rect(x+15,y+10,2,4,DEEP)
    d.rect(x+1,y+3,1,16,WHITE);d.rect(x+18,y+4,1,14,WHITE)
    d.rect(x+4,y+19,12,3,DEEP);d.rect(x+6,y+20,7,1,PALE)
    for xx in range(x+4,x+18,3):d.rect(xx,y,1,2,WHITE)


def _daily_top(d,x,y,v):
    if v%4==0:
        d.slab(x,y+2,20,19,4,PALE,STEEL)
        d.rect(x+5,y+7,11,3,DEEP)
        d.path(f'M{x+8} {y+9}V{y+4}h3V{y+2}h5v4h-3v3z',WHITE)
    elif v%4==1:
        d.rect(x+1,y,18,23,PALE);d.rect(x+3,y+2,14,3,DEEP)
        for xx in (x+4,x+11):
            d.rect(xx,y+7,5,12,INK);d.rect(xx+1,y+6,3,2,STEEL)
            d.rect(xx,y+10,5,5,SAGE);d.rect(xx+1,y+16,3,2,PALE)
    elif v%4==2:
        d.rect(x+2,y,16,23,STEEL);d.rect(x+3,y+1,14,20,PALE)
        d.rect(x+9,y+7,3,12,DEEP);d.rect(x+8,y+3,5,7,WHITE)
        for yy in (y+4,y+6,y+8):d.rect(x+9,yy,4,1,SAGE)
        d.rect(x+4,y+21,12,2,DEEP)
    else:
        # Soap bottle top: rounded cap and shoulders, with a short south wall.
        d.oval(x+2,y+2,16,20,SAGE);d.oval(x+5,y,10,8,INK)
        d.rect(x+5,y+10,10,7,PALE);d.rect(x+7,y+12,6,2,DEEP)
        d.rect(x+4,y+7,2,10,WHITE);d.rect(x+5,y+20,10,2,STEEL)


def _shelf(kind):
    h=240 if kind in ('snacks','noodles') else 210
    d=_Drawing();lip=28 if h==240 else 24
    d.slab(6,7,116,h-13,lip,STEEL,DARK)
    south=7+h-13-lip
    wall_case=kind=='daily'
    # Island gondolas have a Y-axis centre ridge and two horizontal decks.
    # The wall-side daily-goods case instead has its backboard at the RIGHT.
    if wall_case:
        d.rect(12,15,98,south-20,DEEP)
        d.rect(111,12,9,south-10,INK);d.rect(112,13,6,south-13,PALE)
        d.rect(112,13,2,south-13,WHITE)
    else:
        d.rect(12,15,44,south-20,DEEP);d.rect(74,15,42,south-20,DEEP)
        d.rect(58,12,14,south-10,INK);d.rect(60,12,10,south-12,STEEL)
        d.rect(61,13,7,south-15,PALE);d.rect(61,13,2,south-15,WHITE)
        d.rect(54,15,2,south-20,INK);d.rect(74,15,2,south-20,INK)
        d.rect(114,15,2,south-20,PALE)
    d.rect(12,15,2,south-20,PALE)
    painters={'snacks':_bag_top,'noodles':_cup_top,'bread':_bread_top,'daily':_daily_top}
    rows=7 if h==240 else 6
    d.start('class="stock-response"')
    columns=(14,37,60,83) if wall_case else (15,36,75,96)
    for row in range(rows):
        yy=19+row*26
        for col,xx in enumerate(columns):
            if kind=='snacks' and row==4 and col==1:continue
            # Packaging faces the adjacent aisle. The south-facing package
            # drawing is rotated exactly 90 degrees, never an isometric skew.
            angle=90 if wall_case or col<2 else -90
            d.start(f'transform="translate({xx+10} {yy+11}) rotate({angle}) translate(-10 -11)"')
            painters[kind](d,0,0,row*3+col)
            d.end()
    d.end()
    for row in range(1,rows):
        yy=17+row*26
        if wall_case:d.rect(14,yy,95,1,STEEL)
        else:d.rect(14,yy,40,1,STEEL);d.rect(76,yy,38,1,STEEL)
    for yy in range(25,south-14,29):
        d.rect(10,yy,3,12,WHITE);d.rect(11,yy+3,1,4,DEEP)
        if not wall_case:
            d.rect(115,yy,3,12,PALE);d.rect(116,yy+3,1,4,DEEP)
    d.rect(10,south,108,3,PALE);d.rect(13,south+6,101,lip-12,DEEP)
    d.rect(18,south+9,40,2,STEEL);d.rect(69,south+9,40,2,STEEL)
    if not wall_case:d.rect(62,south+3,5,lip-7,INK)
    d.rect(13,h-8,8,5,INK);d.rect(105,h-8,8,5,INK)
    return d,130,h


def _chair_top(d,x,y,w=48,h=40,back_south=False):
    d.oval(x+1,y+5,w,h-2,INK)
    if back_south:d.start(f'transform="rotate(180 {x+w/2:g} {y+h/2:g})"')
    # Overhead seat, arm rests and the narrow top edge of the backrest.
    d.oval(x+8,y+10,w-16,h-15,STEEL)
    d.oval(x+10,y+11,w-20,h-19,SAGE)
    d.rect(x+6,y+2,w-12,8,INK);d.rect(x+8,y+3,w-16,4,PALE)
    d.rect(x+1,y+13,5,h-20,INK);d.rect(x+2,y+13,3,h-22,STEEL)
    d.rect(x+w-6,y+13,5,h-20,INK);d.rect(x+w-5,y+13,3,h-22,STEEL)
    d.rect(x+w//2-2,y+h-5,4,6,STEEL)
    d.rect(x+9,y+h-2,w-18,2,INK)
    if back_south:d.end()


def _keyboard_top(d,x,y):
    d.slab(x,y,67,22,4,PALE,STEEL)
    for row in range(3):
        for col in range(10):d.rect(x+4+col*6,y+4+row*4,4,3,STEEL)
    d.rect(x+19,y+16,27,2,DEEP);d.rect(x+50,y+16,11,2,STEEL)


def _monitor_top(d,kind):
    # CRT depth is on the floor plane; the viewer sees the top housing. The
    # green display is only a compressed strip on the southern face.
    d.slab(72,12,78,48,14,DARK,STEEL)
    d.rect(79,17,64,20,DEEP);d.rect(81,18,60,2,STEEL)
    for yy in (23,27,31):d.rect(88,yy,47,1,INK)
    d.rect(76,46,70,11,INK)
    d.parts.append('<svg x="79" y="48" width="64" height="7" viewBox="0 0 64 28" preserveAspectRatio="none" overflow="hidden">')
    d.rect(0,0,64,28,'#17432f')
    d.start('class="screen-response"')
    if kind=='cctvdesk':
        for yy in (3,15):
            for xx in (3,34):
                d.rect(xx,yy,27,10,DEEP);d.rect(xx+2,yy+2,21,2,SAGE)
                d.rect(xx+2,yy+6,14,2,MINT)
        d.start('class="ambient cctv-scan"');d.rect(1,1,62,2,MINT);d.end()
    else:
        d.start('class="ambient terminal-type"')
        for yy,ww in ((3,41),(9,53),(15,32),(21,46)):d.rect(4,yy,ww,2,MINT)
        d.end()
    d.end();d.parts.append('</svg>')
    d.rect(132,58,4,1,MINT)
    d.rect(105,60,11,4,STEEL);d.oval(93,63,36,8,INK);d.oval(96,64,30,4,STEEL)


def _desk(kind):
    d=_Drawing()
    # The desk's plan occupies most of the drawing; short front fascia below.
    d.slab(8,7,204,108,11,PALE,STEEL)
    d.rect(15,15,190,84,SAGE,'opacity=".22"')
    d.rect(17,18,40,28,DEEP);d.rect(20,21,34,22,STEEL)
    d.rect(23,24,28,2,PALE);d.rect(23,30,19,2,PALE)
    _monitor_top(d,kind)
    # Tower viewed mainly from above, with slots on its narrow south panel.
    d.slab(167,16,32,66,10,STEEL,DEEP)
    for xx in range(173,193,4):d.rect(xx,24,2,34,DARK)
    d.rect(173,73,18,2,INK);d.rect(173,77,12,1,INK);d.rect(193,77,2,2,MINT)
    _keyboard_top(d,72,76)
    d.oval(149,77,13,20,INK);d.oval(151,78,9,16,STEEL);d.rect(155,79,1,7,DEEP)
    d.path('M155 77v-7h-11v-4','none',f'stroke="{INK}" stroke-width="1"')
    # Open ledger from overhead: two pages, spine and tightly aligned writing.
    d.rect(19,53,43,43,STEEL);d.rect(21,51,19,41,WHITE);d.rect(41,51,19,41,PALE)
    d.rect(39,52,2,39,DEEP)
    for yy in range(57,86,6):d.rect(24,yy,12,1,SAGE);d.rect(44,yy,12,1,STEEL)
    d.rect(25,95,32,2,DEEP);d.rect(28,95,5,1,MINT)
    # Overhead coffee cup and handle; the liquid is visible inside the rim.
    d.oval(178,87,15,12,WHITE);d.oval(181,89,9,7,DEEP)
    d.path('M192 90h5v6h-5','none',f'stroke="{PALE}" stroke-width="2"')
    d.rect(17,106,57,3,DEEP);d.rect(151,106,48,3,DEEP)
    _chair_top(d,86,116,50,40,back_south=True)
    return d,220,160


def _toilet():
    d=_Drawing();d.shadow(20,12,61,118)
    # Tank top, lid seam and flush buttons; just a thin front lip beneath.
    d.slab(25,10,53,31,6,WHITE,PALE)
    d.rect(30,15,43,18,PALE);d.rect(31,15,41,2,WHITE)
    d.oval(57,21,9,5,STEEL);d.rect(61,21,1,5,PALE)
    d.rect(33,39,37,7,PALE)
    # The oval seat is a true plan view, with the water bowl visible inside it.
    d.oval(21,45,61,77,STEEL);d.oval(23,44,57,72,WHITE)
    d.oval(32,52,39,55,PALE);d.oval(35,56,33,46,INK)
    d.oval(39,63,25,33,DEEP);d.oval(42,76,19,16,STEEL)
    d.rect(31,44,6,7,SAGE);d.rect(66,44,6,7,SAGE)
    d.rect(25,67,2,25,PALE);d.rect(75,67,2,25,PALE)
    d.path('M35 117h32v5h-5v4H40v-4h-5z',PALE)
    # Handrail and paper holder are small overhead wall-side fixtures.
    d.path('M10 40v72h7','none',f'stroke="{INK}" stroke-width="7"')
    d.path('M10 40v71h7','none',f'stroke="{PALE}" stroke-width="4"')
    d.rect(85,59,5,24,STEEL);d.oval(82,62,15,13,WHITE)
    d.oval(83,65,4,7,STEEL);d.rect(88,74,8,10,PALE);d.rect(89,82,6,2,WHITE)
    return d,100,140


def _cup_on_table(d,x,y,thermos=False):
    d.oval(x,y+3,16,15,STEEL);d.oval(x,y,16,14,WHITE)
    d.oval(x+3,y+2,10,9,DEEP if not thermos else STEEL)
    if thermos:d.rect(x+5,y+5,6,2,PALE)
    else:d.path(f'M{x+15} {y+4}h5v6h-5','none',f'stroke="{PALE}" stroke-width="2"')


def _breaktable():
    d=_Drawing();_chair_top(d,76,0,48,36)
    d.slab(22,34,158,73,9,PALE,STEEL)
    # Compartmented bento is horizontal and viewed through its open top.
    d.slab(45,46,51,36,4,INK,DEEP)
    d.rect(49,50,21,25,WHITE);d.rect(73,50,18,11,DEEP);d.rect(73,64,18,11,SAGE)
    d.rect(56,59,4,3,STEEL);d.rect(77,52,5,3,PALE);d.rect(82,67,5,4,WHITE)
    d.rect(104,49,31,30,STEEL);d.rect(107,52,25,24,PALE);d.rect(109,54,21,1,WHITE)
    d.rect(47,88,49,2,DEEP);d.rect(48,92,49,2,DEEP)
    _cup_on_table(d,145,75)
    _cup_on_table(d,31,75,True)
    d.start('class="ambient break-steam"')
    d.path('M150 76v-6h3v-5h-3v-6h3v-5h2v7h-3v5h3v7z',WHITE,'opacity=".65"');d.end()
    _chair_top(d,75,109,49,34,back_south=True)
    d.path('M88 121h18l4 4v10H89l-4-8z',SAGE);d.rect(97,123,3,10,DEEP)
    return d,200,145


def _carton_top(d,x,y,w,h,opened=False):
    d.slab(x,y,w,h,5,SAGE,STEEL)
    if opened:
        d.rect(x+4,y+4,w-8,h-13,INK)
        d.rect(x+3,y+2,w-6,5,PALE);d.rect(x+3,y+h-14,w-6,5,PALE)
        d.rect(x+3,y+7,5,h-21,STEEL);d.rect(x+w-8,y+7,5,h-21,STEEL)
        d.rect(x+11,y+11,8,7,WHITE);d.rect(x+23,y+12,8,8,DEEP)
    else:
        d.rect(x+w//2-2,y+2,4,h-8,PALE)
        d.rect(x+3,y+(h-6)//2,w-6,2,DEEP)
        d.rect(x+5,y+6,10,7,WHITE);d.rect(x+7,y+8,6,2,STEEL)


def _stockrack():
    d=_Drawing();d.slab(5,6,119,155,17,STEEL,DARK)
    d.rect(11,12,107,128,DEEP)
    # Topmost rack is loaded with cartons and open returnable crates.
    for yy in (17,58,99):
        _carton_top(d,15,yy,44,35,yy==58)
        if yy!=58:
            _carton_top(d,68,yy,44,35,False)
        else:
            d.slab(68,yy,44,35,5,STEEL,DEEP)
            d.rect(72,yy+4,36,24,DARK)
            for xx in range(75,108,6):d.rect(xx,yy+6,2,19,SAGE)
            d.rect(75,yy+11,28,2,STEEL);d.rect(75,yy+20,28,2,STEEL)
        d.rect(11,yy+36,107,2,PALE)
    for xx in (7,118):d.rect(xx,10,4,149,PALE)
    for xx in (8,118):
        for yy in (10,140):d.rect(xx,yy,4,5,INK);d.rect(xx+1,yy+1,2,2,WHITE)
    d.rect(14,146,97,9,DEEP);d.rect(20,147,37,2,STEEL);d.rect(69,147,36,2,STEEL)
    return d,130,170


def _lockers():
    d=_Drawing();d.slab(5,9,110,72,15,STEEL,DEEP)
    # Three deep locker tops. Doors are compressed to a short south edge.
    for col in range(3):
        xx=8+col*35
        d.rect(xx,13,32,50,SAGE if col==1 else STEEL)
        d.rect(xx+2,15,28,2,PALE);d.rect(xx+29,14,1,48,DEEP)
        d.rect(xx+2,66,28,12,STEEL);d.rect(xx+23,69,3,6,PALE)
        d.rect(xx+4,69,13,1,DARK);d.rect(xx+4,72,13,1,DARK)
        d.rect(xx+4,75,9,1,DARK)
    # Only the hanger top, folded shoulders and a short south cloth edge
    # are visible from this camera; never a full upright apron silhouette.
    d.path('M121 15v-5h5v5l-6 5h12l-6-5','none',f'stroke="{PALE}" stroke-width="2"')
    d.start('class="ambient locker-coat"')
    d.path('M120 23h12v3h3v11h-18V26h3z',DARK)
    d.path('M121 24h10v3h2v6h-14v-6h2z',SAGE)
    d.rect(121,24,3,6,PALE);d.rect(128,24,2,6,STEEL)
    d.rect(119,34,14,4,DEEP);d.rect(120,34,12,1,PALE)
    d.end();return d,140,96


def _sink():
    d=_Drawing();d.slab(5,8,140,118,13,STEEL,DEEP)
    # Broad inset basins with rims, drains and a tap seen from above.
    for xx in (13,69):
        d.oval(xx,32,48,65,INK);d.oval(xx+3,35,42,58,PALE)
        d.oval(xx+7,39,34,49,STEEL);d.oval(xx+10,43,28,39,DEEP)
        d.oval(xx+19,67,10,9,INK);d.rect(xx+22,69,4,4,STEEL)
        d.path(f'M{xx+21} 43V22h12v17','none',f'stroke="{INK}" stroke-width="6"')
        d.path(f'M{xx+21} 43V22h12v17','none',f'stroke="{PALE}" stroke-width="3"')
        d.rect(xx+12,23,6,4,WHITE)
    d.rect(122,37,16,61,DEEP)
    for yy in range(41,96,7):d.rect(124,yy,12,3,PALE)
    d.oval(125,16,10,15,MINT);d.rect(128,14,4,6,PALE);d.rect(129,14,9,2,WHITE)
    d.rect(15,117,48,3,STEEL);d.rect(77,117,52,3,STEEL)
    return d,150,140


def _cleaning():
    d=_Drawing();d.slab(5,8,53,85,11,STEEL,DEEP)
    d.oval(10,26,43,49,INK);d.oval(13,29,37,42,PALE)
    d.oval(17,33,29,33,STEEL);d.oval(22,48,16,13,DEEP)
    d.path('M27 36V18h15v14','none',f'stroke="{PALE}" stroke-width="4"')
    d.oval(65,82,37,48,INK);d.oval(67,81,33,40,STEEL)
    d.oval(70,85,27,31,DEEP);d.rect(86,86,10,19,PALE)
    for yy in range(89,104,4):d.rect(88,yy,6,2,DEEP)
    d.path('M69 99V77h28v22','none',f'stroke="{PALE}" stroke-width="2"')
    # A mop viewed along its floor-plane shaft, with a spread fibre head.
    d.path('M64 118 78 16','none',f'stroke="{SAGE}" stroke-width="3"')
    d.rect(76,12,4,15,DEEP);d.rect(53,118,23,7,PALE)
    for xx in range(51,80,4):d.rect(xx,124,2,14,STEEL)
    return d,110,150


_KINDS=('snacks','noodles','bread','daily','sysdesk','cctvdesk',
        'toilet','breaktable','stockrack','lockers','sink','cleaning')


def render_furnishing(kind,x,y,w,h):
    """Return a pure-SVG furnishing fitted to the supplied floor-plan bounds."""
    if kind not in _KINDS:raise ValueError(f'Unknown furnishing kind: {kind}')
    if not all(isinstance(v,(int,float)) and isfinite(v) for v in (x,y,w,h)) or w<=0 or h<=0:
        raise ValueError('Furnishing bounds must be finite, with positive width and height')
    if kind in ('snacks','noodles','bread','daily'):drawing,vw,vh=_shelf(kind)
    elif kind in ('sysdesk','cctvdesk'):drawing,vw,vh=_desk(kind)
    else:
        drawing,vw,vh={'toilet':_toilet,'breaktable':_breaktable,'stockrack':_stockrack,
                       'lockers':_lockers,'sink':_sink,'cleaning':_cleaning}[kind]()
    return (f'<g class="furnishing furnishing-{kind}" transform="translate({x:g} {y:g}) scale({w/vw:.6f} {h/vh:.6f})">'
            +''.join(drawing.parts)+'</g>')
