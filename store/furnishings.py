"""Original pixel furnishings, rendered as editable SVG geometry only.

Every kind is drawn on its own small integer grid, then fitted to the supplied
rectangle. There are no bitmap references, fonts, filters or external resources.
"""
from math import isfinite

INK = '#101b1a'
SHADOW = '#182620'
DARK = '#283d33'
DEEP = '#3e5b48'
STEEL = '#6b8174'
SAGE = '#91a58b'
PALE = '#c4d0bb'
WHITE = '#e7ecdc'
MINT = '#50efc2'


class _Drawing:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, fill, attrs=''):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {attrs}/>')

    def path(self, d, fill, attrs=''):
        self.parts.append(f'<path d="{d}" fill="{fill}" {attrs}/>')

    def polygon(self, points, fill, attrs=''):
        coords = ' '.join(f'{x},{y}' for x, y in points)
        self.parts.append(f'<polygon points="{coords}" fill="{fill}" {attrs}/>')

    def start(self, attrs=''):
        self.parts.append(f'<g {attrs}>')

    def end(self):
        self.parts.append('</g>')

    def shadow(self, x, y, w, h):
        self.path(f'M{x+5} {y}h{w-11}v3h6v{h-6}h-5v3h{-w+10}v-3h-5v{-h+6}h5z', INK, 'opacity=".45"')

    def cuboid(self, x, y, w, h, depth=8, top=PALE, front=STEEL, side=DEEP):
        """Front and right faces, with the upper face receding to the right."""
        self.polygon([(x,y+depth),(x+depth,y),(x+w,y),(x+w-depth,y+depth)], top)
        self.rect(x,y+depth,w-depth,h-depth,front)
        self.polygon([(x+w-depth,y+depth),(x+w,y),(x+w,y+h-depth),(x+w-depth,y+h)],side)
        self.rect(x,y+depth,w-depth,2,WHITE)
        self.path(f'M{x} {y+depth}v{h-depth}h{w-depth}l{depth}-{depth}', 'none', f'stroke="{INK}" stroke-width="2"')

    def oval(self, x, y, w, h, fill):
        # Stepped, eight-sided oval; never an anti-aliased raster ellipse.
        a=max(2,w//5); b=max(2,h//4)
        self.polygon([(x+a,y),(x+w-a,y),(x+w,y+b),(x+w,y+h-b),
                      (x+w-a,y+h),(x+a,y+h),(x,y+h-b),(x,y+b)],fill)

    def rail(self, x, y, w):
        self.rect(x,y,w,6,STEEL);self.rect(x,y,w,2,PALE)
        for xx in range(x+5,x+w-10,23):
            self.rect(xx,y+2,14,3,WHITE);self.rect(xx+2,y+3,4,1,DEEP)


def _bag(d, x, y, variant):
    colours=(SAGE,PALE,DEEP,STEEL)
    c=colours[variant%4]
    d.path(f'M{x+3} {y}h12v2h3v3h-2l3 8v12l-3 7H{x+2}l-2-7V{y+13}l3-8H{x+1}v-3h2z',INK)
    d.path(f'M{x+4} {y+4}h10l2 10v10l-2 6H{x+4}l-2-6v-10z',c)
    d.rect(x+3,y+2,13,3,PALE);d.rect(x+3,y+29,13,3,STEEL)
    for xx in range(x+4,x+16,3):
        d.rect(xx,y+1,1,3,WHITE);d.rect(xx,y+30,1,2,INK)
    d.rect(x+4,y+8,11,3,WHITE)
    if variant%3==0:
        d.oval(x+5,y+15,8,8,PALE);d.rect(x+7,y+16,3,2,WHITE);d.rect(x+7,y+22,4,1,STEEL)
    elif variant%3==1:
        d.oval(x+4,y+14,10,9,DEEP);d.rect(x+6,y+16,2,2,PALE);d.rect(x+10,y+19,2,2,PALE)
    else:
        d.rect(x+5,y+14,8,10,DEEP)
        for yy in (y+16,y+20):
            for xx in (x+6,x+10):d.rect(xx,yy,2,2,PALE)
    d.rect(x+3,y+12,2,12,WHITE,'opacity=".45"')


def _cup(d, x, y, variant):
    d.path(f'M{x} {y+6}h21l-3 23-3 3H{x+7}l-3-3z',INK)
    d.path(f'M{x+2} {y+7}h17l-3 22H{x+6}z',PALE if variant%2 else SAGE)
    d.rect(x+4,y+13,13,9,DEEP);d.rect(x+7,y+15,7,2,WHITE);d.rect(x+6,y+19,9,1,PALE)
    d.oval(x,y+1,21,8,WHITE);d.oval(x+3,y+3,15,3,SAGE)
    d.rect(x+16,y+1,6,2,PALE);d.rect(x+5,y+27,12,2,STEEL)
    d.rect(x+4,y+10,2,16,WHITE,'opacity=".5"')


def _bread(d, x, y, variant):
    # The wrapper's folds remain visible; the food has its own round silhouette.
    d.path(f'M{x+3} {y}h14v3l3 2v25l-3 3H{x+3}l-3-3V{y+5}l3-2z',STEEL)
    d.path(f'M{x+4} {y+3}h12l2 3v23H{x+2}V{y+6}z',PALE)
    if variant%3==0:
        d.oval(x+3,y+9,14,15,SAGE);d.path(f'M{x+5} {y+13}h10v2H{x+5}z',WHITE)
        d.rect(x+7,y+10,2,12,PALE);d.rect(x+12,y+10,2,12,PALE)
    elif variant%3==1:
        d.path(f'M{x+3} {y+23}V{y+13}h2v-3h10v3h2v10z',SAGE)
        d.path(f'M{x+5} {y+22}v-8h2v-2h6v2h2v8z',WHITE)
        d.rect(x+4,y+24,13,2,DEEP)
    else:
        d.oval(x+2,y+10,8,13,SAGE);d.oval(x+10,y+10,8,13,SAGE)
        d.rect(x+4,y+12,3,2,WHITE);d.rect(x+12,y+12,3,2,WHITE)
    d.rect(x+2,y+4,2,24,WHITE);d.rect(x+17,y+6,1,20,WHITE)
    d.rect(x+4,y+26,12,5,DEEP);d.rect(x+6,y+27,8,1,PALE)
    for xx in range(x+5,x+17,3):d.rect(xx,y,1,3,WHITE)


def _daily(d, x, y, variant):
    if variant%4==0:
        d.cuboid(x,y+11,21,20,4,PALE,STEEL,DEEP)
        d.path(f'M{x+8} {y+16}v-7h3V{y+6}h5v7h-3v3z',WHITE)
        d.rect(x+3,y+19,11,7,SAGE);d.rect(x+5,y+21,7,2,WHITE)
    elif variant%4==1:
        d.rect(x+2,y+2,17,30,PALE);d.rect(x+4,y+4,13,4,DEEP)
        for xx in (x+5,x+12):
            d.rect(xx,y+12,5,15,INK);d.rect(xx+1,y+10,3,2,STEEL)
            d.rect(xx,y+14,5,6,SAGE);d.rect(xx+1,y+22,3,3,PALE)
        d.rect(x+4,y+29,13,1,STEEL)
    elif variant%4==2:
        d.rect(x+2,y+1,16,31,STEEL);d.rect(x+4,y+3,12,26,PALE)
        d.rect(x+9,y+8,3,19,DEEP);d.rect(x+8,y+5,5,8,WHITE)
        for yy in (y+6,y+8,y+10):d.rect(x+9,yy,4,1,SAGE)
        d.rect(x+6,y+28,9,2,DEEP)
    else:
        d.rect(x+6,y,9,4,INK);d.rect(x+5,y+4,11,3,WHITE)
        d.path(f'M{x+5} {y+7}h11v3h3v20h-17V{y+10}h3z',SAGE)
        d.rect(x+4,y+14,13,10,PALE);d.rect(x+7,y+17,7,3,DEEP)
        d.rect(x+3,y+11,2,16,WHITE);d.rect(x+5,y+29,12,2,STEEL)


def _shelf(kind):
    height=240 if kind in ('snacks','noodles') else 210
    d=_Drawing();d.shadow(6,17,120,height-20)
    d.cuboid(5,5,117,height-14,11,PALE,DEEP,DARK)
    d.rect(9,19,99,height-37,DARK)
    # Pegboard holes are grouped and sparse, not random single-pixel noise.
    for yy in range(26,height-28,16):
        for xx in range(16,105,14):d.rect(xx,yy,2,2,DEEP)
    for xx in (6,106):
        d.rect(xx,17,4,height-25,STEEL);d.rect(xx,17,1,height-25,PALE)
        for yy in range(31,height-25,12):d.rect(xx+1,yy,2,3,INK)
    rows=5 if height==240 else 4
    pitch=39 if height==240 else 41
    painters={'snacks':_bag,'noodles':_cup,'bread':_bread,'daily':_daily}
    d.start('class="stock-response"')
    for row in range(rows):
        yy=23+row*pitch
        for col,xx in enumerate((13,36,60,84)):
            # Slightly varied facings and a few absent products make stock read
            # as individual packages, while keeping the organised shop rhythm.
            variant=row*3+col
            if kind=='snacks' and row==3 and col==2:continue
            painters[kind](d,xx,yy+(2 if (row+col)%4==0 else 0),variant)
    d.end()
    for row in range(rows):
        yy=58+row*pitch
        d.rail(9,yy,99)
        d.polygon([(108,yy),(119,yy-10),(119,yy-4),(108,yy+6)],STEEL)
    d.rect(10,height-22,98,8,INK);d.rect(14,height-20,90,2,STEEL)
    d.rect(13,height-12,8,7,INK);d.rect(99,height-12,8,7,INK)
    return d,128,height


def _keyboard(d,x,y):
    d.path(f'M{x+4} {y}h57l5 12H{x}z',INK)
    d.path(f'M{x+5} {y+1}h55l3 9H{x+2}z',PALE)
    for row,yy in enumerate((y+3,y+6)):
        for xx in range(x+6+row,x+58,6):d.rect(xx,yy,4,2,STEEL)
    d.rect(x+18,y+9,25,1,STEEL)


def _chair(d,x,y):
    d.shadow(x-3,y+16,51,35)
    d.rect(x+21,y+27,5,18,STEEL)
    d.path(f'M{x+23} {y+42}h-16v3h34v-3H{x+26}v-11h-3z',INK)
    d.rect(x+5,y+43,7,5,INK);d.rect(x+35,y+43,7,5,INK)
    d.oval(x+3,y+11,41,19,INK);d.oval(x+6,y+12,34,14,DEEP)
    d.path(f'M{x+5} {y+18}V{y+3}h4V{y}h30v3h4v15h-4V{y+5}H{x+9}v13z',INK)
    d.path(f'M{x+10} {y+3}h27v15H{x+10}z',STEEL)
    d.rect(x+12,y+4,23,2,SAGE);d.rect(x+11,y+17,25,2,DARK)
    d.rect(x,y+15,4,14,STEEL);d.rect(x+43,y+15,4,14,STEEL)


def _desk(kind):
    d=_Drawing();d.shadow(12,72,204,79)
    # Legs and a shallow drawer unit, behind the tabletop.
    for xx in (18,177):d.rect(xx,88,8,46,INK);d.rect(xx+1,92,3,38,STEEL)
    d.cuboid(140,92,45,42,8,STEEL,DARK,INK)
    for yy in (105,117):d.rect(145,yy,29,1,STEEL);d.rect(153,yy+3,12,2,PALE)
    d.polygon([(10,92),(32,62),(211,62),(189,92)],PALE)
    d.rect(10,92,179,9,STEEL)
    d.polygon([(189,92),(211,62),(211,71),(189,101)],DEEP)
    d.path('M10 92h179l22-30','none',f'stroke="{WHITE}" stroke-width="2"')
    # A real separate monitor and stand, never a kiosk cabinet.
    d.polygon([(67,20),(74,12),(143,12),(150,20),(150,65),(143,72),(67,72)],INK)
    d.polygon([(139,19),(146,17),(147,61),(140,66)],STEEL)
    d.rect(70,21,69,46,STEEL);d.rect(73,24,63,37,INK)
    d.path('M78 27h52v2h3v26h-3v3H78v-3h-2V29h2z','#17432f')
    d.rect(81,30,47,1,DEEP);d.rect(78,29,1,25,SAGE)
    d.start('class="screen-response"')
    if kind=='cctvdesk':
        for yy in (32,44):
            for xx in (81,106):
                d.rect(xx,yy,21,9,DEEP);d.rect(xx+2,yy+2,16,1,SAGE)
                d.rect(xx+2,yy+5,10,1,MINT);d.rect(xx+14,yy+6,4,1,PALE)
        d.start('class="ambient cctv-scan"');d.rect(80,31,49,1,MINT);d.end()
    else:
        d.start('class="ambient terminal-type"')
        for xx,yy,ww in ((81,32,36),(81,37,43),(81,42,27),(81,47,39)):
            d.rect(xx,yy,ww,2,MINT)
        d.rect(81,53,5,2,WHITE);d.end()
    d.end()
    d.rect(99,72,12,7,STEEL);d.oval(88,77,35,5,INK)
    d.rect(123,63,4,2,MINT)
    # Small tower, optical-drive slot, power indicator and ventilation.
    d.cuboid(160,26,31,53,7,PALE,STEEL,DEEP)
    d.rect(164,37,16,3,INK);d.rect(164,44,16,2,DARK)
    d.rect(166,52,5,5,INK);d.rect(168,53,2,2,MINT)
    for yy in (61,65,69):d.rect(165,yy,14,2,DARK)
    _keyboard(d,68,83)
    d.oval(139,85,10,7,STEEL);d.rect(143,86,1,3,INK)
    d.path('M144 85v-4h-7v-4h-5','none',f'stroke="{INK}" stroke-width="1"')
    # Open ledger, bent corners, ruler and paper clip on the other side.
    d.path('M28 69h18l4 2 3-2h17v16H53l-3 2-4-2H28z',WHITE)
    d.rect(48,72,2,13,STEEL)
    for yy in (73,77,81):d.rect(31,yy,13,1,SAGE);d.rect(54,yy,12,1,SAGE)
    d.rect(32,88,27,2,DEEP)
    d.oval(131,71,12,6,INK);d.rect(132,73,10,8,PALE);d.oval(133,71,8,4,DEEP)
    d.path('M142 74h4v5h-4','none',f'stroke="{PALE}" stroke-width="2"')
    _chair(d,78,109)
    return d,220,160


def _toilet():
    d=_Drawing();d.shadow(10,17,83,119)
    # Tiled rear splashback and a clear floor around the pan.
    d.polygon([(11,17),(24,7),(89,7),(89,48),(77,58),(11,58)],PALE)
    for yy in (20,34,47):d.rect(13,yy,64,1,SAGE)
    for xx in (31,51,71):d.rect(xx,13,1,42,SAGE)
    d.cuboid(29,22,44,35,8,WHITE,PALE,STEEL)
    d.oval(34,22,34,9,WHITE);d.rect(56,26,8,3,STEEL)
    d.rect(35,49,25,10,PALE)
    # Pedestal has its own projecting shadow and inset front face.
    d.path('M36 77h29l-3 35-7 7H42l-7-7z',PALE)
    d.path('M55 81h10l-3 31-7 7h-7l7-8z',STEEL)
    d.oval(23,55,53,45,STEEL);d.oval(25,53,48,40,WHITE)
    d.oval(33,61,32,24,STEEL);d.oval(36,65,26,16,INK)
    d.oval(39,67,20,11,DEEP);d.rect(28,70,3,13,PALE)
    # Visible hinges and seat bumpers keep the seat separate from the bowl.
    d.rect(32,55,5,5,SAGE);d.rect(60,55,5,5,SAGE)
    d.rect(25,78,5,3,PALE);d.rect(68,78,4,3,PALE)
    # Grab rail, paper spindle and a short hanging sheet.
    d.path('M16 48v39h7','none',f'stroke="{INK}" stroke-width="7"')
    d.path('M16 48v38h7','none',f'stroke="{PALE}" stroke-width="4"')
    d.rect(79,55,5,24,STEEL);d.rect(77,65,15,4,INK)
    d.oval(77,59,14,13,WHITE);d.oval(78,61,4,8,STEEL)
    d.rect(82,68,9,15,PALE);d.rect(83,80,7,2,WHITE)
    d.rect(32,123,37,4,INK,'opacity=".35"')
    return d,100,140


def _mug(d,x,y):
    d.oval(x,y,15,6,WHITE);d.rect(x+1,y+3,13,15,STEEL)
    d.rect(x+3,y+4,4,12,PALE);d.oval(x+1,y+15,13,5,DEEP)
    d.rect(x+3,y+1,9,2,INK)
    d.path(f'M{x+14} {y+6}h5v8h-5','none',f'stroke="{PALE}" stroke-width="2"')


def _breaktable():
    d=_Drawing();d.shadow(7,37,187,99)
    # One tucked-in chair at the back, another pulled out in front.
    d.rect(71,13,49,8,INK);d.rect(74,16,43,21,STEEL);d.rect(76,18,39,3,SAGE)
    d.rect(76,37,6,20,INK);d.rect(109,37,6,20,INK)
    for xx in (25,151):d.rect(xx,72,8,48,INK);d.rect(xx+1,73,3,43,STEEL)
    d.polygon([(16,76),(40,38),(185,38),(161,76)],PALE)
    d.rect(16,76,145,8,STEEL);d.polygon([(161,76),(185,38),(185,46),(161,84)],DEEP)
    d.path('M16 76h145l24-38','none',f'stroke="{WHITE}" stroke-width="2"')
    # Bento tray with rice and two side dishes, its lid laid beside it.
    d.path('M54 46h44l5 6-7 18H48l-3-6z',INK)
    d.path('M56 49h38l4 4-5 13H52l-3-4z',PALE)
    d.rect(54,52,19,11,WHITE);d.rect(76,51,15,5,DEEP);d.rect(76,59,14,5,SAGE)
    d.rect(62,55,3,2,STEEL);d.rect(81,52,4,2,PALE)
    d.path('M104 54h24l-5 15H99z',STEEL);d.path('M107 57h17l-3 9h-17z',PALE)
    d.rect(57,72,43,2,DEEP);d.rect(58,75,43,1,DEEP)
    _mug(d,139,44)
    d.start('class="ambient break-steam"')
    d.path('M145 43v-6h3v-5h-3v-6h3v-5h2v7h-3v5h3v7z',WHITE,'opacity=".65"');d.end()
    # Thermos and folded jacket on a second chair.
    d.oval(30,49,12,5,INK);d.rect(31,51,10,17,STEEL);d.rect(33,53,2,12,PALE);d.oval(31,65,10,4,DEEP)
    _chair(d,70,90)
    d.path('M82 96h17l5 4v13H84l-4-8z',SAGE);d.rect(92,98,3,13,DEEP)
    return d,200,140


def _carton(d,x,y,w,h,open_top=False):
    d.cuboid(x,y,w,h,5,SAGE,STEEL,DEEP)
    d.rect(x+w//2-2,y+5,4,h-5,PALE)
    d.rect(x+4,y+11,min(12,w-9),9,PALE);d.rect(x+6,y+13,min(7,w-13),2,DEEP)
    if open_top:
        d.path(f'M{x} {y+6}l-3-7h{w-5}l3 7z',PALE)
        d.path(f'M{x+w-5} {y+6}l8-7v{h-4}l-8 6z',SAGE)
        d.rect(x+6,y+4,w-12,4,INK)


def _stockrack():
    d=_Drawing();d.shadow(4,17,123,147)
    d.cuboid(5,6,117,150,10,STEEL,DARK,DEEP)
    d.rect(10,20,99,128,SHADOW)
    for row,yy in enumerate((28,71,114)):
        if row!=1:
            _carton(d,15,yy,39,32,row==0);_carton(d,59,yy+4,43,28)
        else:
            for xx in (15,62):
                d.cuboid(xx,yy+2,41,29,5,STEEL,DEEP,DARK)
                d.rect(xx+3,yy+7,31,3,PALE)
                for bx in range(xx+5,xx+32,6):d.rect(bx,yy+14,3,12,STEEL)
                d.rect(xx+13,yy+8,12,3,INK)
        d.rail(9,yy+33,100)
        d.polygon([(109,yy+33),(120,yy+23),(120,yy+28),(109,yy+39)],STEEL)
    for xx in (6,108):
        d.rect(xx,17,4,145,PALE)
        for yy in range(23,151,11):d.rect(xx+1,yy,2,3,DEEP)
    d.rect(8,159,8,7,INK);d.rect(102,159,8,7,INK)
    return d,130,170


def _lockers():
    d=_Drawing();d.shadow(4,11,124,143)
    d.cuboid(5,6,94,143,9,PALE,STEEL,DEEP)
    for col in range(3):
        xx=8+col*27
        d.rect(xx,18,25,122,DARK);d.rect(xx+2,20,21,118,SAGE if col==1 else STEEL)
        d.rect(xx+3,22,19,2,PALE)
        for yy in (29,34,39,119,124,129):d.rect(xx+6,yy,13,2,DARK)
        d.rect(xx+5,47,15,7,PALE);d.rect(xx+8,49,8,2,STEEL)
        d.rect(xx+17,76,4,14,INK);d.rect(xx+18,78,2,9,PALE)
        d.rect(xx+18,93,2,3,INK)
    d.rect(11,149,8,7,INK);d.rect(77,149,8,7,INK)
    # Hanger and apron silhouette, suspended outside the lockers.
    d.path('M104 36v-8h7v5l-7 5-10 8h28l-11-8','none',f'stroke="{PALE}" stroke-width="2"')
    d.start('class="ambient locker-coat"')
    d.path('M101 47h12l2 12 7 6-4 63H95l-5-63 8-6z',DARK)
    d.path('M102 47h9v15l7 5-3 55H98l-4-55 8-5z',SAGE)
    d.rect(101,75,11,20,DEEP);d.rect(102,77,9,2,PALE)
    d.rect(98,66,3,49,PALE);d.rect(113,68,2,49,STEEL)
    d.end()
    return d,130,160


def _sink():
    d=_Drawing();d.shadow(6,28,141,99)
    d.cuboid(6,45,138,74,14,PALE,STEEL,DEEP)
    d.rect(12,67,109,45,STEEL);d.rect(63,67,2,43,DEEP)
    d.rect(51,77,3,15,PALE);d.rect(70,77,3,15,PALE)
    for xx in (17,67):
        d.oval(xx,43,42,27,INK);d.oval(xx+3,46,36,20,STEEL);d.oval(xx+7,49,28,13,DEEP)
        d.rect(xx+21,56,4,3,INK)
    for xx in (33,82):
        d.path(f'M{xx} 50V29h14v12','none',f'stroke="{INK}" stroke-width="7"')
        d.path(f'M{xx} 50V29h14v12','none',f'stroke="{PALE}" stroke-width="4"')
        d.rect(xx-8,44,6,4,STEEL)
    d.rect(112,42,22,27,DEEP)
    for xx in range(115,133,4):d.rect(xx,45,2,20,PALE)
    d.rect(117,27,10,16,MINT);d.rect(120,23,5,5,PALE);d.rect(120,22,10,2,PALE)
    d.rect(17,120,6,9,INK);d.rect(112,120,6,9,INK)
    return d,150,140


def _cleaning():
    d=_Drawing();d.shadow(4,30,98,109)
    # Low janitor sink has a raised splashback and hose tap.
    d.cuboid(5,43,53,62,9,PALE,STEEL,DEEP)
    d.rect(13,17,39,38,PALE);d.rect(15,20,35,2,WHITE)
    d.oval(12,45,37,28,INK);d.oval(15,48,31,21,STEEL);d.oval(20,52,22,14,DEEP)
    d.path('M30 49V31h12v9','none',f'stroke="{PALE}" stroke-width="4"')
    d.rect(29,30,10,3,STEEL)
    # Bucket, wringer and mop head each have a distinct outline.
    d.path('M63 92h37l-4 40H68z',INK);d.path('M66 94h31l-4 34H71z',STEEL)
    d.oval(63,85,37,13,PALE);d.oval(67,88,29,7,DEEP)
    d.rect(82,86,14,13,SAGE)
    for xx in range(84,96,3):d.rect(xx,88,1,9,DARK)
    d.path('M68 97V79h25v17','none',f'stroke="{INK}" stroke-width="3"')
    d.path('M77 92 90 19','none',f'stroke="{PALE}" stroke-width="4"')
    d.rect(88,13,5,15,DEEP)
    d.path('M62 125h20l4 11H58z',PALE)
    for xx in range(60,86,4):d.rect(xx,131,2,8,STEEL)
    d.path('M70 127 61 39','none',f'stroke="{SAGE}" stroke-width="3"')
    return d,110,150


_KINDS = ('snacks','noodles','bread','daily','sysdesk','cctvdesk',
          'toilet','breaktable','stockrack','lockers','sink','cleaning')


def render_furnishing(kind, x, y, w, h):
    """Return an original SVG group fitted to ``x, y, w, h``.

    Supported kinds: snacks, noodles, bread, daily, sysdesk, cctvdesk, toilet,
    breaktable, stockrack, lockers, sink, cleaning. Animated subgroups use the
    existing store CSS hooks; all other detail is static geometry.
    """
    if kind not in _KINDS:
        raise ValueError(f'Unknown furnishing kind: {kind}')
    if not all(isinstance(v,(int,float)) and isfinite(v) for v in (x,y,w,h)) or w<=0 or h<=0:
        raise ValueError('Furnishing bounds must be finite, with positive width and height')
    if kind in ('snacks','noodles','bread','daily'):
        drawing,vw,vh=_shelf(kind)
    elif kind in ('sysdesk','cctvdesk'):
        drawing,vw,vh=_desk(kind)
    else:
        drawing,vw,vh={'toilet':_toilet,'breaktable':_breaktable,
                       'stockrack':_stockrack,'lockers':_lockers,
                       'sink':_sink,'cleaning':_cleaning}[kind]()
    return (f'<g class="furnishing furnishing-{kind}" transform="translate({x:g} {y:g}) scale({w/vw:.6f} {h/vh:.6f})">'
            + ''.join(drawing.parts) + '</g>')
