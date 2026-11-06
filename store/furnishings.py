"""Original code-drawn furnishings for the 57store night-shift interior.

RPG oblique view: horizontal floor axes, visible top depth, upright front
surfaces and contact shadows. Everything is SVG geometry in eight colours;
reference photographs and game screenshots are never embedded in the output.
"""
from math import isfinite

INK = SHADOW = '#0a0b0c'
DARK = '#131415'
DEEP = '#25292b'
STEEL = '#50595c'
SAGE = '#879393'
PALE = '#bdc7c5'
WHITE = '#e0e6e2'
MINT = '#53efc0'


class _Drawing:
    def __init__(self): self.parts = []
    def rect(self, x, y, w, h, fill, attrs=''):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {attrs}/>')
    def path(self, points, fill, attrs=''):
        self.parts.append(f'<path d="{points}" fill="{fill}" {attrs}/>')
    def polygon(self, points, fill, attrs=''):
        self.parts.append('<polygon points="' + ' '.join(f'{x},{y}' for x,y in points) + f'" fill="{fill}" {attrs}/>')
    def start(self, attrs=''): self.parts.append(f'<g {attrs}>')
    def end(self): self.parts.append('</g>')
    def oval(self, x, y, w, h, fill):
        # Stepped outline: deliberately no smooth Bezier/ellipse edges.
        a=max(2, round(w/5)); b=max(2, round(h/4))
        self.polygon([(x+a,y),(x+w-a,y),(x+w,y+b),(x+w,y+h-b),
                      (x+w-a,y+h),(x+a,y+h),(x,y+h-b),(x,y+b)],fill)
    def shadow(self, x, y, w, h):
        self.rect(x,y,w,h,SHADOW,'opacity=".45"')
    def box(self, x, y, w, depth, height, top=PALE, front=STEEL, side=DEEP):
        """A top plane and a substantial front; a 4px right edge gives thickness."""
        self.rect(x,y,w,depth+height,INK)
        self.rect(x+2,y+2,w-6,depth-2,top)
        self.rect(x+2,y+depth,w-6,height-2,front)
        self.rect(x+w-4,y+3,3,depth+height-5,side)
        self.rect(x+3,y+3,w-8,2,WHITE)
        self.rect(x+2,y+depth,w-6,2,PALE)
    def rail(self, x, y, w):
        self.rect(x,y,w,6,INK)
        self.rect(x,y,w,2,PALE)
        self.rect(x+1,y+2,w-2,3,STEEL)
        for xx in range(int(x)+4,int(x+w)-13,25):
            self.rect(xx,y+2,11,3,WHITE)
            self.rect(xx+2,y+3,4,1,DEEP)


def _bag(d,x,y,v):
    # Inflated snack pouch: crimped top, shoulders, dark fold and rolled seam.
    body=(STEEL,SAGE,PALE)[v%3]
    d.path(f'M{x+3} {y}h16v3h2v5h2v15h-2v5H{x+2}v-5H{x}V{y+8}h2V{y+3}h1z',INK)
    d.path(f'M{x+4} {y+4}h13l3 5v12l-3 4H{x+5}l-3-4V{y+9}z',body)
    d.rect(x+3,y+1,16,3,PALE);d.rect(x+3,y+25,17,3,STEEL)
    for xx in range(x+4,x+18,3):d.rect(xx,y,1,3,WHITE)
    d.rect(x+4,y+7,2,14,WHITE);d.rect(x+18,y+10,2,12,DEEP)
    d.rect(x+7,y+8,9,3,DEEP)
    if v%3==0:
        d.oval(x+7,y+13,10,7,WHITE);d.rect(x+10,y+15,5,2,SAGE)
    elif v%3==1:
        for xx,yy in ((7,14),(12,18),(13,13)):
            d.oval(x+xx,y+yy,5,4,PALE);d.rect(x+xx+1,y+yy+1,2,1,DEEP)
    else:
        d.rect(x+7,y+14,10,7,DEEP);d.rect(x+9,y+15,2,2,SAGE);d.rect(x+13,y+18,2,2,SAGE)


def _noodle(d,x,y,v):
    # Thin oval foil lid over a visibly tapered upright cup, never a flat disc.
    d.path(f'M{x+1} {y+7}h22l-3 20H{x+4}z',INK)
    d.path(f'M{x+3} {y+9}h18l-3 16H{x+6}z',PALE if v%2 else SAGE)
    d.path(f'M{x+18} {y+10}h3l-3 15h-3z',STEEL)
    d.rect(x+5,y+13,14,7,DEEP);d.rect(x+7,y+15,9,2,WHITE)
    d.rect(x+8,y+23,9,2,STEEL)
    d.oval(x,y,24,10,INK);d.oval(x+1,y+1,22,7,WHITE)
    d.oval(x+4,y+2,16,4,PALE if v%2 else SAGE)
    d.rect(x+9,y+3,7,2,DEEP);d.rect(x+20,y+1,5,3,PALE)


def _bread(d,x,y,v):
    # The clear wrapper is represented by its thin folded outline, not a slab.
    d.path(f'M{x+3} {y}h19v3h2v24H{x+1}V{y+3}h2z',STEEL)
    d.rect(x+2,y+4,22,21,PALE,'opacity=".22"')
    if v%3==0:
        # Square sliced toast with curved upper crust and a stacked heel.
        d.path(f'M{x+5} {y+24}V{y+9}h2V{y+5}h13v4h2v15z',SAGE)
        d.path(f'M{x+7} {y+21}V{y+10}h2V{y+7}h9v3h2v11z',WHITE)
        d.rect(x+20,y+10,2,13,STEEL);d.rect(x+8,y+23,13,2,STEEL)
    elif v%3==1:
        # Two round rolls, scored crowns and a darker lower crust.
        d.oval(x+4,y+7,18,16,SAGE);d.oval(x+5,y+7,16,11,PALE)
        d.rect(x+8,y+9,11,2,WHITE);d.rect(x+12,y+8,2,9,SAGE)
        d.rect(x+5,y+21,16,2,STEEL)
    else:
        # Bent crescent, folded segments, tapering tips.
        d.path(f'M{x+3} {y+14}h3V{y+9}h4V{y+6}h9v3h4v5h2v8h-4v-4h-3v-3h-7v3H{x+7}v4H{x+3}z',SAGE)
        d.rect(x+10,y+7,4,8,WHITE);d.rect(x+16,y+9,4,7,PALE)
        d.rect(x+6,y+12,3,7,PALE);d.rect(x+21,y+17,3,5,STEEL)
    d.rect(x+3,y+3,1,22,WHITE);d.rect(x+23,y+5,1,20,WHITE)
    d.rect(x+3,y+1,20,2,PALE);d.rect(x+6,y+24,15,3,DEEP)
    d.rect(x+9,y+25,7,1,WHITE)


def _daily(d,x,y,v):
    if v%4==0:
        d.box(x,y+10,26,8,16,PALE,SAGE,STEEL)
        d.rect(x+6,y+13,14,3,DEEP)
        d.path(f'M{x+9} {y+15}V{y+6}h4V{y+3}h8v6h-5v6z',WHITE)
        d.rect(x+5,y+23,15,4,WHITE);d.rect(x+7,y+24,7,1,STEEL)
    elif v%4==1:
        d.rect(x+2,y,23,34,INK);d.rect(x+3,y+1,21,32,PALE)
        d.rect(x+7,y+3,13,3,DEEP)
        for xx in (x+6,x+15):
            d.rect(xx+2,y+10,3,3,STEEL);d.rect(xx,y+12,7,18,DEEP)
            d.rect(xx,y+17,7,8,SAGE);d.rect(xx+1,y+13,2,3,WHITE)
    elif v%4==2:
        d.rect(x+5,y,17,34,STEEL);d.rect(x+6,y+2,15,30,PALE)
        d.rect(x+12,y+11,3,19,DEEP);d.rect(x+10,y+4,7,10,WHITE)
        for yy in (y+5,y+8,y+11):d.rect(x+11,yy,5,1,SAGE)
        d.rect(x+7,y+30,12,3,DEEP)
    else:
        d.path(f'M{x+7} {y+8}h13v4h4v18h-3v3H{x+5}v-3H{x+3}V{y+12}h4z',SAGE)
        d.rect(x+8,y+5,11,6,DEEP);d.rect(x+11,y+2,4,5,PALE)
        d.rect(x+12,y+1,12,3,WHITE);d.rect(x+7,y+17,13,10,PALE)
        d.rect(x+9,y+19,9,2,DEEP);d.rect(x+5,y+14,2,15,WHITE)


def _gondola(kind):
    d=_Drawing(); painter=_bag if kind=='snacks' else _noodle
    d.shadow(17,40,160,176)
    # Four tall uprights and the two deck footprints flank a raised centre.
    d.rect(7,34,164,180,INK);d.rect(11,37,156,169,DARK)
    d.rect(12,38,69,144,STEEL);d.rect(99,38,67,144,STEEL)
    d.rect(14,41,64,137,DEEP);d.rect(101,41,62,137,DEEP)
    # Upright central backboard is 30px above its foot; a solid light top cap.
    d.rect(79,8,22,178,INK);d.rect(82,10,16,165,STEEL)
    d.rect(83,10,13,7,PALE);d.rect(84,11,11,2,WHITE)
    d.rect(83,18,4,157,SAGE);d.rect(96,18,3,158,DARK)
    # Long decks run north/south. Raised inner trays sit beside the spine;
    # lower outer trays reach toward the two separate customer aisles.
    for xx in (14,102):
        d.rect(xx,33,62,145,SAGE)
        d.rect(xx+3,36,56,140,STEEL)
        d.rect(xx+4,37,53,1,PALE)
    for xx in (48,103):
        d.rect(xx,24,29,151,DEEP)
        d.rect(xx+2,25,25,146,STEEL)
        d.rect(xx+2,25,2,146,PALE)
    # Individual faces remain legible at phone size. The inner row is raised
    # beside the spine, while the outer row projects toward each aisle.
    d.start('class="stock-response"')
    for row in range(4):
        yy=17+row*41
        for col,xx in enumerate((17,49,105,137)):
            if kind=='snacks' and row==2 and col==0:continue
            painter(d,xx,yy+(5 if col in (0,3) else 0),row+col)
    d.end()
    # Continuous rail edges, rather than a ladder of horizontal facades,
    # make this read as a lengthwise double-sided island shelf.
    for xx,yy,hh in ((13,39,141),(45,28,148),(100,28,148),(162,39,141)):
        d.rect(xx,yy,4,hh,INK);d.rect(xx,yy,2,hh,PALE)
        for label_y in range(yy+13,yy+hh-12,39):
            d.rect(xx-1,label_y,5,10,WHITE)
            d.rect(xx,label_y+3,2,4,STEEL)
    d.rail(13,178,64);d.rail(103,178,61)
    for xx in (7,166):
        d.rect(xx,30,6,178,INK);d.rect(xx+1,31,3,174,PALE)
        for yy in (48,90,132,174):d.rect(xx+1,yy,3,2,STEEL)
    # Substantial south end panel: its face and projecting foot convey height.
    d.rect(10,182,158,29,INK);d.rect(13,184,152,23,STEEL)
    d.rect(15,185,148,3,PALE);d.rect(18,191,139,13,DEEP)
    d.rect(24,194,55,5,SAGE);d.rect(97,194,52,5,SAGE)
    d.rect(84,185,10,22,DARK);d.rect(85,185,6,3,WHITE)
    d.rect(9,208,160,7,DEEP);d.rect(14,208,150,2,SAGE)
    d.rect(17,214,12,5,INK);d.rect(149,214,12,5,INK)
    return d,180,220


def _front_shelf(kind):
    d=_Drawing(); wide=kind=='bread'; w=180 if wide else 130; h=145 if wide else 180
    top=28 if wide else 34; rows=3
    d.shadow(9,25,w-12,h-27)
    d.box(5,7,w-10,top,h-top-15,STEEL,DEEP,DARK)
    d.rect(12,12,w-27,top-8,SAGE);d.rect(13,13,w-30,2,PALE)
    d.rect(12,top+8,w-25,h-top-30,DARK)
    # A few products stand on the deep top shelf, breaking the silhouette.
    # Their bases overlap the top lip, as objects do in the reference camera.
    d.start('class="stock-response"')
    if wide:
        for col in (0,1,3,4):
            d.start(f'transform="translate({18+col*30} 3) scale(.8 .8)"')
            _bread(d,0,0,col);d.end()
    else:
        for col in (0,2):
            d.start(f'transform="translate({17+col*32} 2) scale(.85 .85)"')
            _daily(d,0,0,col);d.end()
    d.end()
    # Deep shelves have visible undersides; vertical perforated steel posts.
    step=32 if wide else 43
    d.start('class="stock-response"')
    for row in range(rows):
        yy=top+3+row*step
        for col in range(5 if wide else 3):
            xx=15+col*(31 if wide else 33)
            (_bread if wide else _daily)(d,xx,yy,row+col)
    d.end()
    for row in range(rows):d.rail(11,top+31+row*step,w-23)
    for xx in (6,w-13):
        d.rect(xx,top+2,6,h-top-13,INK);d.rect(xx+1,top+3,3,h-top-17,PALE)
        for yy in range(top+11,h-16,13):d.rect(xx+1,yy,2,2,STEEL)
    d.rect(11,h-12,w-23,7,DEEP);d.rect(12,h-12,w-25,2,SAGE)
    d.rect(14,h-5,10,4,INK);d.rect(w-26,h-5,10,4,INK)
    return d,w,h


def _chair(d,x,y,front=False):
    # An office chair has an upright padded back, visible seat and caster base.
    d.shadow(x+2,y+43,47,14)
    d.rect(x+22,y+35,6,18,STEEL);d.rect(x+9,y+50,33,3,INK)
    d.rect(x+22,y+48,6,11,INK);d.rect(x+5,y+52,8,5,INK);d.rect(x+38,y+52,8,5,INK)
    if not front:
        d.box(x+6,y,39,9,22,STEEL,DEEP,DARK)
        d.rect(x+11,y+12,29,14,STEEL);d.rect(x+13,y+13,25,2,SAGE)
    d.oval(x+5,y+25,41,22,INK);d.oval(x+7,y+26,37,16,STEEL)
    d.oval(x+10,y+27,31,10,SAGE);d.rect(x+9,y+43,32,3,DARK)
    for xx in (x+1,x+44):d.rect(xx,y+21,5,19,INK);d.rect(xx+1,y+22,3,10,PALE)
    if front:
        d.box(x+6,y+30,39,8,24,STEEL,DEEP,DARK)
        d.rect(x+11,y+40,28,12,STEEL);d.rect(x+24,y+40,2,10,SAGE)


def _keyboard(d,x,y):
    d.box(x,y,66,12,4,PALE,STEEL,DEEP)
    for row in range(3):
        for col in range(10):d.rect(x+4+col*6,y+3+row*3,4,2,STEEL)
    d.rect(x+20,y+12,25,2,DEEP);d.rect(x+50,y+12,10,2,STEEL)


def _monitor(d,kind,x=72,y=5):
    d.shadow(x+3,y+54,76,12)
    d.box(x,y,78,18,43,STEEL,PALE,DEEP)
    # Cooling slits in the deep CRT shell and a recognisable substantial screen.
    for yy in (y+5,y+9,y+13):d.rect(x+13,yy,48,2,DEEP)
    d.rect(x+5,y+21,66,33,INK);d.rect(x+8,y+24,60,26,DARK)
    d.parts.append(f'<svg x="{x+8}" y="{y+24}" width="60" height="26" viewBox="0 0 60 26" overflow="hidden">')
    d.start('class="screen-response"')
    if kind=='cctvdesk':
        for xx in (2,31):
            for yy in (2,14):
                d.rect(xx,yy,26,10,DEEP);d.rect(xx+2,yy+2,20,2,SAGE)
                d.rect(xx+2,yy+6,11,2,MINT)
        d.start('class="ambient cctv-scan"');d.rect(0,1,60,2,MINT);d.end()
    else:
        d.start('class="ambient terminal-type"')
        for yy,ww in ((4,35),(10,47),(16,28),(22,41)):d.rect(4,yy,ww,2,MINT)
        d.end()
    d.end();d.parts.append('</svg>')
    d.rect(x+58,y+56,4,2,MINT);d.rect(x+65,y+56,3,2,STEEL)
    d.rect(x+31,y+61,16,6,STEEL);d.oval(x+20,y+65,39,9,INK)
    d.oval(x+23,y+65,33,5,SAGE)


def _desk(kind):
    d=_Drawing()
    d.shadow(14,90,196,57)
    # Drawer pedestal, open knee space, legs and front apron are all visible.
    d.rect(14,88,7,49,INK);d.rect(15,91,4,41,STEEL)
    d.rect(198,88,7,49,INK);d.rect(199,91,3,41,STEEL)
    d.box(20,90,47,9,42,STEEL,SAGE,DEEP)
    for yy in (105,120):
        d.rect(24,yy,37,1,DEEP);d.rect(37,yy+4,12,3,DEEP)
    d.box(7,31,207,58,14,PALE,STEEL,DEEP)
    d.rect(11,36,195,46,SAGE)
    d.rect(13,37,190,2,PALE)
    _monitor(d,kind)
    # Small separate computer tower with drive, ventilation and status diode.
    d.box(172,21,31,19,51,SAGE,STEEL,DEEP)
    d.rect(177,44,19,5,INK);d.rect(178,45,17,1,PALE)
    d.rect(177,53,18,3,DEEP);d.rect(180,61,3,3,MINT)
    for yy in (65,68,71,74):d.rect(185,yy,11,1,INK)
    _keyboard(d,74,80)
    d.oval(149,80,13,17,INK);d.oval(151,81,9,12,PALE)
    d.rect(155,82,1,6,STEEL)
    d.path('M155 80v-6h-10v-5','none',f'stroke="{INK}" stroke-width="1"')
    # Open ruled ledger and pencil on the desk, with a tiny page thickness.
    d.box(20,60,42,27,3,SAGE,STEEL,DEEP)
    d.rect(22,60,18,25,WHITE);d.rect(42,60,17,25,PALE)
    d.rect(40,61,2,23,STEEL)
    for yy in range(65,82,5):d.rect(25,yy,11,1,SAGE);d.rect(45,yy,11,1,STEEL)
    d.rect(22,91,35,2,DEEP);d.rect(24,91,5,1,MINT)
    d.oval(36,42,16,11,WHITE);d.oval(39,44,10,5,DEEP)
    d.rect(37,50,14,8,PALE);d.rect(39,56,10,2,STEEL)
    d.path('M51 48h5v6h-5','none',f'stroke="{PALE}" stroke-width="2"')
    _chair(d,85,115,front=True)
    return d,220,180


def _toilet():
    d=_Drawing();d.shadow(20,111,64,25)
    # Tank's deep lid, vertical ceramic body and side flush lever.
    d.box(24,8,54,15,39,WHITE,PALE,STEEL)
    d.rect(29,12,42,7,PALE);d.rect(30,12,40,2,WHITE)
    d.rect(77,29,7,5,SAGE);d.rect(78,29,5,2,WHITE)
    # Raised oval lid. Its thick rim stands behind the seat, as in the photo.
    d.oval(27,27,49,52,STEEL);d.oval(29,28,45,48,WHITE)
    d.oval(34,33,35,37,PALE);d.rect(35,35,32,3,WHITE)
    d.rect(29,72,8,6,SAGE);d.rect(65,72,8,6,SAGE)
    # Pedestal is narrower than the projecting bowl and reaches the floor.
    d.path('M32 92h40v17l-5 23H41l-7-9z',STEEL)
    d.path('M34 94h34v17l-6 19H43l-7-10z',PALE)
    d.rect(39,113,3,12,WHITE);d.rect(44,129,18,3,SAGE)
    d.path('M19 79h65v24l-7 14H32l-10-11z',STEEL)
    d.path('M22 82h57v20l-6 11H35l-10-10z',PALE)
    d.oval(18,68,66,37,STEEL);d.oval(20,67,62,34,WHITE)
    d.oval(29,73,44,22,SAGE);d.oval(33,77,36,15,DEEP)
    d.oval(39,80,25,10,PALE);d.oval(44,82,16,7,STEEL)
    d.rect(24,85,3,11,PALE);d.rect(74,84,3,11,PALE)
    # Integrated washlet controls belong to the bowl, not to a fixed wall.
    d.box(8,72,13,16,6,PALE,STEEL,DEEP)
    for yy in (76,80,84):d.rect(12,yy,5,2,DEEP)
    return d,100,140


def _table_cup(d,x,y,thermos=False):
    if thermos:
        d.path(f'M{x+4} {y+3}h11v25h-2v3H{x+6}v-3H{x+4}z',INK)
        d.rect(x+5,y+6,9,23,STEEL);d.rect(x+6,y+7,2,20,PALE)
        d.oval(x+3,y,13,7,INK);d.oval(x+4,y+1,11,4,SAGE)
    else:
        d.rect(x+1,y+5,15,13,PALE);d.oval(x+2,y+14,13,7,SAGE)
        d.oval(x,y,17,10,WHITE);d.oval(x+3,y+2,11,5,DEEP)
        d.path(f'M{x+16} {y+7}h5v8h-5','none',f'stroke="{PALE}" stroke-width="2"')


def _breaktable():
    d=_Drawing();_chair(d,76,0)
    d.shadow(27,93,154,46)
    for xx in (29,167):
        d.rect(xx,96,7,40,INK);d.rect(xx+1,97,4,35,SAGE)
    d.box(21,44,160,57,12,PALE,STEEL,DEEP)
    d.rect(25,49,151,46,SAGE);d.rect(27,51,147,2,PALE)
    d.box(43,58,53,29,5,INK,DEEP,INK)
    d.rect(47,61,22,22,WHITE);d.rect(72,61,19,10,STEEL);d.rect(72,74,19,9,PALE)
    d.rect(56,70,4,3,STEEL);d.rect(76,63,6,3,PALE)
    d.rect(77,76,5,3,STEEL);d.rect(84,77,4,3,WHITE)
    d.rect(44,94,52,2,DEEP);d.rect(45,98,52,2,DEEP)
    d.box(103,62,29,25,3,PALE,STEEL,DEEP);d.rect(107,66,21,16,STEEL)
    _table_cup(d,145,74);_table_cup(d,30,58,True)
    d.start('class="ambient break-steam"')
    d.path('M151 74v-7h3v-5h-3v-5h3v-6h2v8h-3v5h3v7z',PALE);d.end()
    _chair(d,75,110,front=True)
    return d,200,172


def _carton(d,x,y,w=41,depth=14,height=24,opened=False):
    d.box(x,y,w,depth,height,SAGE,STEEL,DEEP)
    if opened:
        d.rect(x+5,y+4,w-12,depth-3,INK)
        d.rect(x+2,y+1,w-7,4,PALE);d.rect(x+3,y+depth-2,w-8,4,PALE)
        d.rect(x+7,y+6,8,5,WHITE);d.rect(x+20,y+5,9,5,STEEL)
    else:
        d.rect(x+w//2-2,y+2,4,depth-2,PALE)
        d.rect(x+w//2-2,y+depth,4,height-3,SAGE)
    d.rect(x+6,y+depth+6,14,9,PALE)
    d.rect(x+8,y+depth+8,8,1,DEEP);d.rect(x+8,y+depth+11,6,1,DEEP)
    d.rect(x+6,y+depth+height-6,w-15,2,DEEP)


def _stockrack():
    d=_Drawing();d.shadow(10,25,116,141)
    d.rect(8,13,111,145,DARK);d.rect(13,16,101,140,DEEP)
    d.rect(10,8,108,12,STEEL);d.rect(11,9,104,3,PALE)
    for yy in (19,64,109):
        _carton(d,17,yy,42,13,23,yy==64)
        if yy==64:
            d.box(66,yy+4,43,14,21,STEEL,DEEP,DARK)
            for xx in range(71,105,7):d.rect(xx,yy+20,3,14,SAGE)
            d.rect(70,yy+19,34,2,PALE);d.rect(70,yy+28,34,2,STEEL)
        else:_carton(d,66,yy,42,13,23)
        d.rail(11,yy+38,106)
    for xx in (6,117):
        d.rect(xx,8,6,155,INK);d.rect(xx+1,9,3,153,PALE)
        for yy in range(23,157,11):d.rect(xx+1,yy,2,2,STEEL)
    d.rect(8,161,11,6,INK);d.rect(109,161,11,6,INK)
    return d,130,170


def _lockers():
    d=_Drawing();d.shadow(9,32,120,123)
    d.box(5,7,112,36,111,SAGE,STEEL,DEEP)
    # Doors retain the metal grille, lock and full human-height proportion.
    for col in range(3):
        xx=9+col*35
        d.rect(xx,45,32,105,INK);d.rect(xx+1,46,29,101,STEEL)
        d.rect(xx+2,47,27,2,SAGE)
        for yy in (52,56,60,129,133):d.rect(xx+5,yy,19,2,DEEP)
        d.rect(xx+23,83,4,12,PALE);d.rect(xx+24,86,2,3,INK)
        d.rect(xx+7,69,14,6,PALE);d.rect(xx+9,71,7,2,STEEL)
    d.rect(7,152,108,6,DARK);d.rect(12,157,8,5,INK);d.rect(103,157,8,5,INK)
    # A hanging apron now has a vertical body, consistent with the RPG view.
    d.path('M123 47v-5h5v5l-8 6h16l-8-6','none',f'stroke="{PALE}" stroke-width="2"')
    d.start('class="ambient locker-coat"')
    d.path('M122 55h10v13h4v43h-18V68h4z',DEEP)
    d.path('M124 57h6v14h4v37h-14V71h4z',SAGE)
    d.rect(122,82,10,9,STEEL);d.rect(123,83,8,1,PALE)
    d.rect(122,103,10,3,STEEL);d.end()
    return d,140,170


def _sink():
    d=_Drawing();d.shadow(13,87,132,49)
    for xx in (12,134):d.rect(xx,83,6,52,INK);d.rect(xx+1,84,3,47,STEEL)
    d.box(5,25,140,63,17,PALE,STEEL,DEEP)
    d.rect(10,30,130,52,SAGE)
    for xx in (13,68):
        d.oval(xx,42,46,35,INK);d.oval(xx+2,42,42,31,PALE)
        d.oval(xx+6,46,34,24,STEEL);d.oval(xx+10,48,26,17,DEEP)
        d.oval(xx+20,58,8,5,INK);d.rect(xx+22,59,4,1,SAGE)
        d.path(f'M{xx+22} 49V20h12v10','none',f'stroke="{INK}" stroke-width="7"')
        d.path(f'M{xx+22} 47V21h11v9','none',f'stroke="{PALE}" stroke-width="4"')
        d.rect(xx+17,31,8,4,STEEL);d.rect(xx+18,31,6,2,WHITE)
    d.rect(119,42,18,35,DEEP)
    for yy in range(45,75,6):d.rect(121,yy,14,3,PALE)
    d.rect(26,110,99,5,STEEL);d.rect(26,111,99,2,PALE)
    d.rect(35,116,76,8,DEEP);d.rect(44,116,56,2,SAGE)
    d.rect(122,21,10,16,SAGE);d.rect(124,17,6,6,PALE)
    d.rect(125,16,12,3,WHITE)
    return d,150,140


def _cleaning():
    d=_Drawing();d.shadow(10,110,92,32)
    d.box(5,27,53,39,31,PALE,STEEL,DEEP)
    d.oval(11,38,39,24,INK);d.oval(13,39,35,20,PALE)
    d.oval(17,42,27,14,STEEL);d.oval(24,49,12,5,INK)
    d.path('M29 44V16h14v13','none',f'stroke="{INK}" stroke-width="7"')
    d.path('M29 44V17h13v12','none',f'stroke="{PALE}" stroke-width="4"')
    d.rect(11,97,6,32,DEEP);d.rect(47,97,6,32,DEEP)
    # Mop bucket: open water surface, tapered body and separate wringer.
    d.path('M64 98h38l-4 35H70z',INK)
    d.path('M67 102h32l-4 28H73z',STEEL)
    d.oval(63,91,40,17,INK);d.oval(65,92,36,13,SAGE)
    d.oval(68,95,30,8,DEEP);d.rect(87,93,12,12,PALE)
    for yy in (96,100):d.rect(89,yy,8,2,STEEL)
    d.path('M67 104V82h31v22','none',f'stroke="{PALE}" stroke-width="2"')
    d.path('M64 126 80 23','none',f'stroke="{SAGE}" stroke-width="4"')
    d.path('M65 124 80 25','none',f'stroke="{PALE}" stroke-width="1"')
    d.rect(78,16,5,15,DEEP);d.rect(53,125,24,6,PALE)
    for xx in range(50,80,4):d.rect(xx,131,3,13,SAGE)
    return d,110,150


_KINDS = ('snacks','noodles','bread','daily','sysdesk','cctvdesk',
          'toilet','breaktable','stockrack','lockers','sink','cleaning')


def render_furnishing(kind,x,y,w,h):
    """Return an original pure-SVG sprite fitted inside the supplied bounds."""
    if kind not in _KINDS: raise ValueError(f'Unknown furnishing kind: {kind}')
    if not all(isinstance(v,(int,float)) and isfinite(v) for v in (x,y,w,h)) or w<=0 or h<=0:
        raise ValueError('Furnishing bounds must be finite, with positive width and height')
    if kind in ('snacks','noodles'): drawing,vw,vh=_gondola(kind)
    elif kind in ('bread','daily'): drawing,vw,vh=_front_shelf(kind)
    elif kind in ('sysdesk','cctvdesk'): drawing,vw,vh=_desk(kind)
    else:
        drawing,vw,vh={'toilet':_toilet,'breaktable':_breaktable,'stockrack':_stockrack,
                       'lockers':_lockers,'sink':_sink,'cleaning':_cleaning}[kind]()
    return (f'<g class="furnishing furnishing-{kind}" transform="translate({x:g} {y:g}) scale({w/vw:.6f} {h/vh:.6f})">'
            + ''.join(drawing.parts) + '</g>')
