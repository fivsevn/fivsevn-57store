"""Original modern-store sprites drawn in SVG, with an oblique RPG camera.

The visible lid, raised housing and overlapping shelves establish height. Glass
and shadows alone use alpha; every solid belongs to the store's eight colours.
The shop references inform construction, never supply website image assets.
"""
from html import escape

INK = BLACK = '#0a0b0c'
DARK = '#131415'
DEEP = '#25292b'
STEEL = '#50595c'
MID = '#879393'
PALE = '#bdc7c5'
WHITE = '#e0e6e2'
MINT = '#53efc0'


class Drawing:
    def __init__(self): self.parts = []

    def rect(self, x, y, w, h, color, opacity=None):
        if w <= 0 or h <= 0: return
        op = '' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"{op}/>')

    def path(self, value, color, opacity=None):
        op = '' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<path d="{value}" fill="{color}"{op}/>')

    def poly(self, points, color, opacity=None):
        self.path('M' + ' '.join(f'{x},{y}' for x, y in points) + 'Z', color, opacity)

    def group(self, classes='', transform=''):
        cls = f' class="{classes}"' if classes else ''
        tr = f' transform="{transform}"' if transform else ''
        self.parts.append(f'<g{cls}{tr}>')

    def end(self): self.parts.append('</g>')

    def text(self, x, y, value, size=6, color=MINT):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}">{escape(value)}</text>')

    def body(self, x, y, w, depth, height, top=PALE, face=STEEL):
        """North-up lid, substantial south elevation and narrow right bevel."""
        self.rect(x+3, y+depth+height, w, 4, INK, .4)
        self.rect(x, y, w, depth+height, INK)
        self.rect(x+2, y+2, w-4, depth-2, top)
        self.rect(x+2, y+depth, w-4, height-2, face)
        self.rect(x+2, y+2, w-5, 2, WHITE)
        self.rect(x+2, y+depth-2, w-4, 2, PALE)
        self.rect(x+w-6, y+4, 4, depth+height-6, DEEP)
        self.rect(x+w-6, y+3, 2, depth-3, MID)
        self.rect(x+3, y+depth+1, 2, height-4, MID)

    def vent(self, x, y, cols, rows=1, color=INK, step=4):
        for j in range(rows):
            for i in range(cols): self.rect(x+i*step, y+j*4, 2, 2, color)

    def round(self, x, y, w, h, color):
        c = min(3, w//3, h//3)
        self.path(f'M{x+c} {y}H{x+w-c}v1h{c-1}v{c-1}h1V{y+h-c}h-1v{c-1}h{1-c}v1H{x+c}v-1h{1-c}v{1-c}h-1V{y+c}h1v{1-c}h{c-1}Z', color)

    def bottle(self, x, y, color=PALE, variant=0):
        # Cap, shoulders, bright curved side and a shaded cylindrical foot.
        self.path(f'M{x+4} {y}h5v5h2v3h2v14H{x}V{y+8}h2V{y+5}h2Z', INK)
        self.rect(x+4, y+1, 5, 3, WHITE)
        self.path(f'M{x+4} {y+5}h5v3h2v12H{x+2}V{y+8}h2Z', color)
        self.rect(x+3, y+8, 2, 10, WHITE)
        self.rect(x+9, y+8, 2, 12, STEEL)
        self.rect(x+2, y+12, 9, 5, DEEP if variant % 2 else MID)
        self.rect(x+4, y+13, 5, 2, WHITE)
        self.rect(x+3, y+20, 7, 1, MID)

    def can(self, x, y, color=PALE):
        self.round(x, y+2, 12, 17, STEEL)
        self.rect(x+1, y+4, 10, 12, color)
        self.round(x, y, 12, 6, WHITE)
        self.rect(x+3, y+2, 6, 2, MID)
        self.rect(x+6, y+2, 2, 2, DEEP)
        self.rect(x+2, y+8, 8, 5, DEEP)
        self.rect(x+3, y+9, 5, 2, PALE)
        self.rect(x+2, y+5, 1, 10, WHITE)

    def carton(self, x, y, color=PALE):
        self.path(f'M{x} {y+6}l6-6h7l3 6v18H{x}Z', INK)
        self.rect(x+1, y+7, 14, 16, color)
        self.poly([(x+1,y+6),(x+6,y+1),(x+11,y+6)], WHITE)
        self.poly([(x+11,y+6),(x+6,y+1),(x+12,y+1),(x+15,y+6)], MID)
        self.rect(x+12, y+7, 3, 16, STEEL)
        self.rect(x+2, y+12, 10, 6, DEEP)
        self.rect(x+4, y+13, 6, 2, WHITE)

    def rice(self, x, y, flip=False):
        self.path(f'M{x} {y+16}v-3h2v-3h2v-3h2V{y+4}h2V{y+2}h4v2h2v3h2v3h2v3h2v3Z', STEEL)
        self.path(f'M{x+1} {y+13}v-3h2V{y+7}h3V{y+4}h2V{y+1}h4v3h2v3h3v3h2v3Z', WHITE)
        self.rect(x+(7 if flip else 6), y+8, 7, 7, DEEP)
        self.rect(x+8, y+9, 2, 4, INK)
        self.rect(x+9, y+2, 3, 2, MID)
        self.rect(x+1, y+17, 18, 2, PALE)

    def sandwich(self, x, y):
        self.rect(x, y+2, 22, 19, STEEL)
        self.rect(x+1, y, 20, 18, PALE)
        self.poly([(x+3,y+14),(x+18,y+2),(x+18,y+14)], WHITE)
        self.poly([(x+6,y+14),(x+18,y+5),(x+18,y+8),(x+10,y+14)], MID)
        self.poly([(x+11,y+14),(x+18,y+9),(x+18,y+11),(x+14,y+14)], DEEP)
        self.rect(x+2, y+1, 5, 3, WHITE)
        self.rect(x+2, y+18, 18, 2, WHITE)

    def bento(self, x, y, variant=0):
        self.path(f'M{x+2} {y}h25v2h2v19h-2v2h-25v-2h-2V{y+2}h2Z', INK)
        self.rect(x+2, y+2, 25, 17, PALE)
        self.rect(x+3, y+3, 12, 14, WHITE)
        self.rect(x+14, y+3, 2, 14, STEEL)
        self.rect(x+17, y+3, 9, 6, DEEP)
        self.rect(x+17, y+10, 9, 7, MID)
        self.rect(x+5+variant, y+6, 2, 2, MID)
        self.path(f'M{x+18} {y+12}h5v2h2v2h-7Z', WHITE)
        self.rect(x+18, y+4, 3, 3, PALE)
        self.rect(x+24, y+3, 2, 13, WHITE, .5)
        self.rect(x+4, y+20, 20, 1, STEEL)

    def cup(self, x, y, color=PALE):
        self.path(f'M{x+1} {y+6}h16l-2 15H{x+3}Z', STEEL)
        self.path(f'M{x+2} {y+6}h13l-2 13H{x+4}Z', color)
        self.round(x, y+1, 17, 9, WHITE)
        self.round(x+2, y+3, 13, 5, DEEP)
        self.rect(x+4, y+3, 8, 2, MID)
        self.rect(x+4, y+10, 2, 6, WHITE)

    def bottle_top(self, x, y, color=PALE, variant=0):
        self.round(x, y+3, 14, 19, INK)
        self.round(x+1, y+1, 12, 17, color)
        self.round(x+3, y, 8, 8, WHITE)
        self.round(x+5, y+2, 4, 4, STEEL)
        self.rect(x+3, y+11, 8, 4, DEEP if variant else MID)
        self.rect(x+4, y+12, 5, 1, WHITE)
        self.rect(x+2, y+7, 1, 9, WHITE)

    def carton_top(self, x, y, color=PALE):
        self.rect(x, y+3, 16, 21, STEEL)
        self.rect(x, y, 16, 20, color)
        self.poly([(x,y+7),(x+8,y),(x+16,y+7),(x+8,y+14)], WHITE)
        self.poly([(x,y+7),(x+8,y+14),(x+16,y+7),(x+16,y+12),(x+8,y+18),(x,y+12)], MID)
        self.rect(x+7,y+1,2,13,PALE)
        self.rect(x+2,y+17,12,3,DEEP)
        self.rect(x+4,y+18,7,1,WHITE)

    def cup_top(self, x, y, color=PALE):
        self.round(x,y+3,17,17,STEEL)
        self.round(x,y,17,17,color)
        self.round(x+2,y+2,13,13,WHITE)
        self.round(x+4,y+4,9,9,DEEP)
        self.rect(x+5,y+5,5,2,MID)
        self.rect(x+6,y+10,5,2,PALE)


def _coffee(d):
    d.body(8, 21, 70, 24, 97, STEEL, DARK)
    d.rect(12, 46, 59, 88, INK)
    # Three transparent bean hoppers project above the metal top.
    for index, x in enumerate((16, 34, 52)):
        d.rect(x, 8, 16, 31, INK)
        d.rect(x+1, 10, 14, 8, MID)
        d.rect(x+2, 18, 12, 18, DEEP)
        for k in range(5):
            xx=x+3+(k*3+index)%8; yy=22+(k*5)%12
            d.path(f'M{xx} {yy}h3v1h1v2h-4Z', STEEL)
            d.rect(xx+1, yy, 1, 2, INK)
        d.rect(x+1, 9, 13, 2, PALE)
        d.rect(x+2, 19, 1, 14, WHITE, .45)
        d.rect(x+2, 35, 12, 2, MID)
    d.rect(15, 46, 53, 36, STEEL)
    d.rect(18, 49, 47, 29, INK)
    d.rect(21, 52, 41, 23, DEEP)
    d.group('screen-response')
    for xx in (24, 37, 50):
        for yy in (56, 66):
            d.path(f'M{xx} {yy}h7v4h-1v2h-5v-2h-1Z', PALE)
            d.rect(xx+1, yy+7, 5, 1, MINT)
    d.end()
    # The black dispensing recess is framed by two steel pillars.
    d.rect(16, 86, 51, 41, STEEL)
    d.rect(20, 86, 43, 35, BLACK)
    d.rect(21, 86, 41, 4, DEEP)
    d.rect(35, 88, 15, 5, MID); d.rect(40, 93, 5, 5, INK)
    d.rect(22, 117, 39, 8, MID)
    for xx in range(24, 60, 4): d.rect(xx, 119, 2, 4, INK)
    d.cup(34, 99, WHITE)
    d.group('ambient steam')
    d.path('M42 102v-4h2v-4h-2v-4h2v-3h2v5h-2v4h2v4h-2v2Z', WHITE)
    d.end()
    d.rect(14, 130, 52, 3, DEEP); d.rect(63, 135, 4, 2, MINT)
    for yy in (93, 120):
        d.path(f'M83 {yy+5}h15l-2 19H85Z', STEEL)
        for offset in (4, 8, 12): d.rect(85, yy+offset, 11, 2, PALE)
        d.round(82, yy, 17, 8, WHITE); d.round(85, yy+2, 11, 4, INK)


def _warmer(d):
    d.body(5, 8, 86, 22, 50, PALE, STEEL)
    d.rect(11, 12, 72, 14, MID)
    d.rect(14, 15, 65, 9, DEEP)
    d.rect(11, 32, 72, 39, INK)
    d.rect(15, 34, 64, 33, DEEP)
    d.group('ambient warmer-light')
    d.rect(15, 34, 64, 2, WHITE); d.rect(15, 36, 64, 2, MINT)
    d.end()
    # Two overlapping steel trays, with irregular fried-food silhouettes.
    for yy, variants in ((41, (0,1,0,2)), (57, (1,0,2,0))):
        d.rect(17, yy+7, 59, 3, MID); d.rect(16, yy+10, 61, 3, PALE)
        d.rect(16, yy+13, 61, 2, INK)
        for k, v in enumerate(variants):
            x=20+k*14
            if v == 2:
                d.path(f'M{x} {yy+2}h9v2h2v3H{x-2}v-3h2Z', PALE)
                d.rect(x+1, yy+3, 6, 1, MID)
            else:
                d.path(f'M{x+2} {yy}h5v2h3v4h-2v2h-6v-2h-2v-4h2Z', MID if v else PALE)
                d.rect(x+3, yy+2, 3, 2, WHITE)
    d.rect(12, 31, 2, 39, WHITE); d.rect(80, 31, 2, 39, MID)
    d.rect(46, 33, 2, 36, PALE)
    d.rect(43, 45, 2, 11, WHITE); d.rect(50, 45, 2, 11, WHITE)
    d.poly([(18,36),(22,36),(34,66),(30,66)], WHITE, .13)
    d.rect(11, 73, 71, 3, MID); d.vent(15, 75, 12, color=INK)
    d.rect(76, 75, 4, 2, MINT)


def _checkout(d):
    # Counter has usable depth and a separate, clearly raised front cabinet.
    d.body(5, 38, 190, 56, 45, PALE, STEEL)
    d.rect(10, 42, 178, 48, WHITE)
    d.rect(11, 94, 176, 4, MINT)
    d.rect(12, 101, 81, 29, DARK); d.rect(98, 101, 84, 29, DARK)
    d.rect(16, 104, 73, 3, MID); d.rect(102, 104, 76, 3, MID)
    d.rect(16, 128, 73, 2, DEEP); d.rect(102, 128, 76, 2, DEEP)
    # POS screen is tilted back; pedestal and keyboard sit on the counter.
    d.path('M26 12h54l4 12v33H23V24Z', STEEL)
    d.rect(27, 16, 51, 34, INK); d.rect(31, 20, 43, 26, DEEP)
    d.rect(28, 16, 48, 2, MID)
    d.group('screen-response'); d.group('ambient pos-display')
    d.text(35, 29, 'TOTAL', 6, PALE); d.text(35, 41, '¥ 057', 9, MINT)
    d.end(); d.end()
    d.rect(45, 53, 15, 14, STEEL); d.rect(48, 53, 5, 12, MID)
    d.path('M35 65h37l6 8H30Z', DEEP); d.rect(34, 71, 40, 3, INK)
    d.rect(22, 78, 62, 13, STEEL)
    for yy in (80, 84):
        for xx in range(26, 80, 7): d.rect(xx, yy, 5, 2, PALE)
    d.rect(40, 88, 25, 2, WHITE)
    # Raised receipt printer: lid seams, black paper mouth, paper hanging out.
    d.body(140, 43, 41, 18, 30, PALE, MID)
    d.rect(145, 47, 30, 10, WHITE)
    d.rect(145, 56, 30, 2, STEEL)
    d.rect(144, 63, 29, 5, INK); d.rect(173, 64, 3, 2, MINT)
    d.group('paper-response'); d.group('ambient printer')
    d.path('M147 65h22v22h-2v13h-22v-3h2Z', WHITE)
    for yy, ww in ((71,15),(75,12),(79,16),(84,9),(89,15),(94,12)):
        d.rect(150, yy, ww, 1, STEEL)
    d.end(); d.end()
    d.rect(147, 83, 27, 2, PALE)
    # Hand scanner in a cradle, and the distinct flat payment tray.
    d.rect(101, 66, 20, 19, MID)
    d.path('M97 46h24v18h-7v17h-9V64h-8Z', INK)
    d.rect(100, 49, 18, 7, DEEP); d.rect(101, 49, 16, 2, MINT)
    d.rect(107, 64, 5, 13, STEEL)
    d.path('M113 80h14V59h5v-2h-7v21h-12Z', DARK)
    d.rect(91, 87, 36, 10, STEEL); d.rect(94, 89, 30, 5, DEEP)
    d.round(100, 89, 6, 5, PALE)


def _microwave(d):
    d.body(5, 8, 86, 25, 45, PALE, MID)
    d.rect(11, 12, 73, 17, WHITE)
    d.rect(16, 15, 62, 11, PALE)
    for yy in (17, 21): d.rect(63, yy, 12, 2, STEEL)
    d.rect(10, 37, 55, 33, INK); d.rect(13, 40, 44, 25, DEEP)
    d.rect(16, 43, 38, 19, DARK)
    for yy in range(45, 61, 3):
        for xx in range(18, 53, 3): d.rect(xx, yy, 1, 1, STEEL)
    d.rect(59, 40, 4, 26, PALE); d.rect(60, 41, 2, 23, WHITE)
    d.rect(69, 37, 14, 11, INK)
    d.group('ambient microwave'); d.text(70, 45, '0:57', 5, MINT); d.end()
    for yy in (52, 57):
        d.rect(69, yy, 5, 3, PALE); d.rect(77, yy, 5, 3, STEEL)
    d.rect(70, 64, 11, 5, MINT)
    d.rect(11, 73, 70, 2, STEEL)
    d.rect(14, 78, 10, 3, INK); d.rect(71, 78, 10, 3, INK)


def _magazines(d):
    # North/south rack along the east wall. Covers and retaining lips face WEST;
    # the thick south end and rear legs give the shallow trays physical height.
    d.rect(13, 154, 83, 5, INK, .4)
    d.rect(11, 18, 82, 132, INK)
    d.rect(15, 21, 74, 109, DARK)
    d.rect(81, 9, 14, 141, INK); d.rect(83, 11, 8, 137, MID)
    d.rect(84, 12, 5, 4, WHITE)
    for index, yy in enumerate((24, 59, 94)):
        d.rect(17, yy, 63, 33, STEEL)
        d.rect(21, yy+3, 56, 27, DEEP)
        d.rect(22, yy+3, 54, 2, MID)
        d.group('stock-response')
        for col in range(2):
            # Tilted covers are seen from above, with their reading edge west.
            x=20+col*29; y=yy+4+(col%2)
            d.group(transform=f'translate({x+26} {y}) rotate(90)')
            d.rect(2, 2, 23, 27, INK)
            d.rect(0, 0, 23, 27, (PALE, MID, WHITE)[(index+col)%3])
            d.rect(2, 2, 18, 3, DEEP)
            if (index+col)%3 == 0:
                d.rect(8, 9, 7, 7, STEEL); d.rect(7, 8, 9, 3, INK)
                d.path('M5 17h13v7H3v-5h2Z', DEEP)
            elif (index+col)%3 == 1:
                d.poly([(3,24),(12,9),(20,24)], DEEP)
                d.rect(3, 9, 5, 4, MINT)
            else:
                d.rect(3, 9, 17, 7, DEEP); d.rect(5, 11, 12, 3, PALE)
                for k in range(3): d.rect(3, 20+k*2, 16-k*3, 1, STEEL)
            d.rect(2, 25, 18, 2, WHITE)
            d.end()
        d.end()
        d.rect(13, yy, 6, 32, STEEL); d.rect(13, yy, 2, 30, WHITE)
        d.rect(19, yy+1, 2, 29, INK)
        d.rect(21, yy+31, 59, 3, MID)
    # A raised end board and feet, not another magazine pocket.
    d.rect(13, 131, 69, 20, STEEL)
    d.rect(15, 131, 65, 3, PALE)
    d.rect(17, 137, 61, 10, DEEP)
    d.rect(14, 151, 6, 6, INK); d.rect(84, 151, 6, 6, INK)


def _fresh(d, variant='fresh'):
    east_open = variant == 'dairy'
    # Both directions share one camera. A tall insulated spine stands at the
    # wall; the lit access edge faces the aisle; the south end is a deep panel.
    d.rect(8, 188, 91, 5, INK, .4)
    d.rect(7, 10, 89, 179, INK)
    d.rect(11, 14, 80, 137, STEEL)
    d.rect(13, 17, 76, 130, DARK)
    back_x = 12 if east_open else 80
    open_x = 84 if east_open else 13
    d.rect(back_x, 9, 13, 144, MID)
    d.rect(back_x+2, 11, 9, 137, PALE)
    d.rect(back_x+3, 15, 7, 3, WHITE)
    for yy in range(24, 138, 9): d.rect(back_x+4, yy, 5, 2, STEEL)
    deck_x = 29 if east_open else 20
    d.group('ambient case-light')
    d.rect(open_x, 21, 2, 125, WHITE)
    d.rect(back_x+(13 if east_open else -2), 20, 2, 126, MINT)
    d.end()
    def stock(fn, x, y, width, height, *args):
        # Products face the same access edge as the cabinet. Their visible tops
        # establish a sideways display footprint rather than a front elevation.
        tr = (f'translate({x} {y+width}) rotate(-90)' if east_open else
              f'translate({x+height} {y}) rotate(90)')
        d.group(transform=tr); fn(0, 0, *args); d.end()

    # Four separate deep shelves, not a uniform array of square compartments.
    for row, yy in enumerate((24, 55, 86, 117)):
        d.rect(deck_x, yy+2, 51, 21, DEEP)
        d.rect(deck_x+2, yy+4, 46, 15, STEEL)
        d.rect(deck_x, yy+23, 52, 4, PALE)
        d.rect(deck_x, yy+27, 52, 3, INK)
        d.group('stock-response')
        if variant == 'bento':
            stock(d.bento, deck_x+2, yy-1, 29, 23, row%2)
            if row in (0,2): stock(d.cup_top, deck_x+30, yy+4, 17, 21, PALE)
            else:
                d.rect(deck_x+34, yy+4, 14, 14, INK)
                d.rect(deck_x+35, yy+5, 12, 11, WHITE)
                for yoff in (7,10,13): d.rect(deck_x+37, yy+yoff, 8, 1, MID)
        elif variant == 'dairy':
            if row < 2:
                stock(d.carton_top, deck_x+1, yy+2, 16, 24, WHITE); stock(d.carton_top, deck_x+27, yy+4, 16, 24, PALE)
            elif row == 2:
                stock(d.bottle_top, deck_x+2, yy+6, 13, 22, WHITE, 1); stock(d.bottle_top, deck_x+28, yy+4, 13, 22, PALE, 0)
            else:
                stock(d.cup_top, deck_x+2, yy+3, 17, 21, WHITE); stock(d.cup_top, deck_x+28, yy+4, 17, 21, PALE)
        else:
            stock(d.rice, deck_x+2, yy+2, 20, 19, row%2 == 0)
            if row%2: stock(d.rice, deck_x+28, yy+1, 20, 19, True)
            else: stock(d.sandwich, deck_x+27, yy+1, 22, 21)
        d.end()
        # Forward lip occludes the merchandise base; the edge toward the aisle
        # has a continuous upright retaining rail, unlike the solid back wall.
        d.rect(deck_x, yy+24, 52, 3, MID)
        d.rect(open_x, yy+9, 4, 18, PALE)
        d.rect(open_x+(2 if east_open else 0), yy+11, 2, 11, WHITE)
    # Tall south end exposes cabinet height, thickness and refrigeration base.
    d.path('M10 151h82v34H10Z', STEEL)
    d.rect(13, 155, 75, 21, PALE)
    d.rect(16, 158, 69, 15, MID)
    d.rect(11, 150, 79, 4, WHITE)
    d.rect(15, 178, 70, 5, DEEP)
    d.rect(72, 158, 12, 5, INK); d.text(74,162,'4°',3.5,MINT)
    d.rect(back_x, 151, 12, 33, MID)
    d.rect(open_x, 148, 3, 36, WHITE)
    d.group('ambient glass-light')
    d.rect(open_x+1, 22, 1, 122, WHITE, .5)
    d.end()


def _freezer(d):
    d.body(5, 8, 116, 49, 37, PALE, MID)
    d.rect(11, 14, 104, 37, INK); d.rect(15, 18, 96, 29, DEEP)
    # Deep wire baskets are visible beneath two offset sliding glass lids.
    for x in (17, 64):
        d.rect(x, 19, 43, 26, STEEL)
        d.rect(x+2, 21, 39, 22, DEEP)
        for xx in range(x+3, x+40, 6): d.rect(xx, 21, 1, 22, PALE)
        for yy in (25, 32, 39): d.rect(x+2, yy, 39, 1, MID)
    for x,y in ((21,23),(37,25),(68,22),(85,25)):
        d.path(f'M{x+2} {y}h9v2h2v11h-2v2h-9v-2h-2V{y+2}h2Z', WHITE if x%2 else PALE)
        d.rect(x+3,y+4,7,6,DEEP); d.rect(x+4,y+5,5,2,MID)
    d.group('ambient freezer-light')
    d.rect(13,18,2,28,MINT); d.rect(17,16,93,2,WHITE)
    d.end()
    d.rect(15,18,46,29,PALE,.08); d.rect(64,18,46,29,PALE,.12)
    d.rect(60,14,4,38,PALE); d.rect(61,17,1,29,WHITE)
    d.rect(14,46,97,4,STEEL); d.rect(14,46,97,1,WHITE)
    d.rect(31,40,14,4,STEEL); d.rect(33,39,10,2,WHITE)
    d.rect(81,23,14,4,STEEL); d.rect(83,22,10,2,WHITE)
    d.group('ambient freezer-reflection reflection')
    d.poly([(21,20),(26,20),(42,44),(37,44)],WHITE,.25)
    d.poly([(82,19),(85,19),(103,44),(100,44)],WHITE,.22)
    d.end()
    # Thick pale insulated front with two metal seams and a compressor grille.
    d.rect(12,61,101,22,PALE); d.rect(13,62,97,2,WHITE)
    d.rect(12,83,100,3,STEEL); d.rect(14,87,66,2,PALE)
    d.rect(88,67,22,20,STEEL); d.rect(91,69,16,5,INK)
    d.text(93,73,'-20',3.5,MINT)
    for yy in (77,80,83): d.rect(91,yy,16,1,INK)


def _drinks(d):
    # Customer glass is on the NORTH edge; the camera sees the open replenishing
    # backs from the SOUTH cold room. Do not put handles on the stockroom face.
    d.body(5, 9, 307, 31, 96, STEEL, DARK)
    d.rect(11, 13, 294, 23, PALE)
    for bay in range(3):
        x=13+98*bay
        # Far glass doors and their top rails are seen above the open rear tiers.
        d.rect(x,16,92,18,INK); d.rect(x+3,18,86,13,DEEP)
        d.rect(x+3,18,86,2,WHITE)
        d.rect(x+72,21,12,2,PALE)
        d.rect(x+1,37,92,87,INK); d.rect(x+5,40,84,81,DEEP)
        d.group('ambient drinks-light')
        d.rect(x+5,40,2,80,WHITE); d.rect(x+87,40,2,80,MINT)
        d.end()
        for row in range(3):
            yy=43+row*25
            # Slightly uneven quantities expose the dark depth behind stock.
            for col in range(5-(1 if row==1 and bay==2 else 0)):
                xx=x+10+col*15; v=(row+col+bay)%5
                if v==0:d.carton(xx,yy-1,PALE)
                elif v==1:d.can(xx,yy+3,WHITE)
                else:d.bottle(xx,yy,(PALE,MID,MINT)[(col+bay)%3],v)
            d.rect(x+5,yy+21,84,4,PALE)
            d.rect(x+5,yy+25,84,2,INK)
            # Shelf runners continue backwards into the replenishment opening.
            for xx in (x+23,x+53,x+80):d.rect(xx,yy+22,1,2,STEEL)
        d.rect(x+1,38,3,87,MID); d.rect(x+90,38,3,87,STEEL)
        d.group('ambient drink-reflection reflection')
        d.poly([(x+14,20),(x+18,20),(x+30,30),(x+26,30)],WHITE,.45)
        d.end()
    d.rect(12,127,291,5,STEEL)
    for xx in (20,118,216):
        d.rect(xx,128,76,2,MID)
    d.rect(276,127,25,7,INK); d.text(281,132,'4°C',4,MINT)


_EQUIPMENT = {
    'coffee': (104,150,_coffee),
    'warmer': (96,88,_warmer),
    'checkout': (200,145,_checkout),
    'microwave': (96,88,_microwave),
    'magazines': (104,165,_magazines),
    'fresh': (104,200,_fresh),
    'bento': (104,200,lambda d: _fresh(d,'bento')),
    'dairy': (104,200,lambda d: _fresh(d,'dairy')),
    'freezer': (126,102,_freezer),
    'drinks': (318,146,_drinks),
}


def render_equipment(kind, x, y, w, h):
    """Embed an original equipment sprite, preserving its native aspect ratio."""
    if kind not in _EQUIPMENT: raise ValueError(f'Unknown equipment kind: {kind}')
    if w <= 0 or h <= 0: raise ValueError('Equipment bounds must be positive')
    vw, vh, draw = _EQUIPMENT[kind]
    drawing = Drawing(); draw(drawing)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" '
            f'viewBox="0 0 {vw} {vh}" preserveAspectRatio="xMidYMax meet" '
            f'class="equipment equipment-{kind}" overflow="visible" '
            'shape-rendering="crispEdges" aria-hidden="true">'
            + ''.join(drawing.parts) + '</svg>')
