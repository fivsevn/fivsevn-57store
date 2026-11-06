"""Original code-drawn shop equipment, informed by manufacturers' photographs.

No raster images, external assets, fonts, filters, or gradients are needed. Each
small scene has its own integer drawing grid, with a visible top and right side.
Motion hooks surround only the moving/light-emitting part of an appliance.
"""
from html import escape

INK = '#101b1a'
BLACK = '#091210'
DARK = '#20312e'
DEEP = '#304d40'
STEEL = '#647e74'
MID = '#8ba78d'
PALE = '#bdcdc0'
WHITE = '#e0e8d7'
MINT = '#50efc2'


class Drawing:
    def __init__(self):
        self.parts = []

    def rect(self, x, y, w, h, color, opacity=None):
        if w <= 0 or h <= 0:
            return
        op = '' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"{op}/>')

    def path(self, d, color, opacity=None):
        op = '' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<path d="{d}" fill="{color}"{op}/>')

    def poly(self, pts, color, opacity=None):
        self.path('M' + ' '.join(f'{x},{y}' for x, y in pts) + 'Z', color, opacity)

    def group(self, classes='', transform=''):
        cls = f' class="{classes}"' if classes else ''
        tr = f' transform="{transform}"' if transform else ''
        self.parts.append(f'<g{cls}{tr}>')

    def end(self):
        self.parts.append('</g>')

    def text(self, x, y, value, size=6, color=MINT):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}">{escape(value)}</text>')

    def body(self, x, y, w, h, depth=8, color=PALE, side=STEEL, top=WHITE):
        """Front at (x,y); top recedes up/right, maintaining one perspective."""
        self.poly([(x+5,y+h+3),(x+w+depth+5,y+h+3-depth//2),
                   (x+w+depth+5,y+3),(x+w,y+3),(x,y+h)], BLACK, .4)
        self.poly([(x,y),(x+depth,y-depth//2),(x+w+depth,y-depth//2),(x+w,y)], top)
        self.poly([(x+w,y),(x+w+depth,y-depth//2),(x+w+depth,y+h-depth//2),(x+w,y+h)], side)
        self.rect(x,y,w,h,color)
        self.rect(x,y,w,1,WHITE)
        self.rect(x,y+h-2,w,2,INK)
        self.rect(x+w-2,y,2,h,side)

    def vent(self, x, y, cols, rows=1, color=INK, step=4):
        for j in range(rows):
            for i in range(cols):
                self.rect(x+i*step,y+j*4,2,2,color)

    def label(self, x, y, w, color=WHITE):
        self.rect(x,y,w,3,color)
        self.rect(x+1,y+1,max(1,w-3),1,STEEL)

    def bottle(self, x, y, h=22, color=MID, kind=0):
        # Distinct narrow neck, stepped shoulders, label and glass highlight.
        self.group(transform=f'translate({x} {y})')
        self.rect(3,0,5,2,WHITE if kind%2 else STEEL)
        self.rect(3,2,5,3,color)
        self.path(f'M3 5h5v2h2v{h-9}H1V7h2Z',color)
        self.rect(2,7,2,h-9,PALE,.65)
        self.rect(2,h-11,7,7,WHITE if kind%3 else DEEP)
        self.rect(4,h-9,4,2,DEEP if kind%3 else PALE)
        self.rect(2,h-2,7,2,STEEL)
        if kind%3==2:
            self.rect(5,4,2,3,WHITE)
        self.end()

    def can(self, x, y, h=16, color=PALE):
        self.rect(x+1,y,8,2,STEEL)
        self.rect(x,y+2,10,h-3,color)
        self.rect(x+1,y+h-1,8,1,WHITE)
        self.rect(x+1,y+3,2,h-5,WHITE)
        self.rect(x+4,y+5,5,5,DEEP)
        self.rect(x+5,y+6,3,1,MINT)

    def carton(self, x, y, h=23, color=PALE):
        self.path(f'M{x} {y+4}l4-4h6l3 4v{h-4}h-13Z',color)
        self.poly([(x+4,y),(x+7,y+4),(x+13,y+4),(x+10,y)],WHITE)
        self.rect(x+9,y+5,4,h-5,STEEL)
        self.rect(x+1,y+7,7,7,DEEP)
        self.rect(x+2,y+9,5,2,WHITE)
        self.rect(x+1,y+h-5,7,2,MID)

    def rice(self, x, y, flip=False):
        # Stepped rice triangle, transparent wrapper corners, seaweed strip.
        self.path(f'M{x} {y+19}v-4h2v-4h2v-4h2V{y+3}h2V{y+1}h4v2h2v4h2v4h2v4h2v4Z',PALE)
        self.path(f'M{x+3} {y+16}v-4h2V{y+8}h2V{y+5}h5v3h2v4h2v4Z',WHITE)
        self.rect(x+(7 if flip else 6),y+10,7,9,DEEP)
        self.rect(x+8,y+11,2,6,INK)
        self.rect(x+1,y+20,18,2,STEEL)
        self.rect(x+9,y+3,3,2,MID)

    def sandwich(self, x, y):
        self.path(f'M{x} {y+21}V{y+2}h2v-2h17v2h2v19Z',PALE)
        self.poly([(x+2,y+18),(x+17,y+3),(x+17,y+18)],WHITE)
        self.poly([(x+6,y+18),(x+17,y+7),(x+17,y+10),(x+9,y+18)],MID)
        self.poly([(x+10,y+18),(x+17,y+11),(x+17,y+14),(x+13,y+18)],DEEP)
        self.rect(x+2,y+20,17,2,STEEL)
        self.rect(x+3,y+3,5,3,WHITE)

    def bento(self, x, y, variant=0):
        self.path(f'M{x+2} {y}h25v2h2v17h-2v2h-25v-2h-2V{y+2}h2Z',INK)
        self.rect(x+2,y+2,25,16,PALE)
        self.rect(x+3,y+3,12,13,WHITE)
        self.rect(x+14,y+3,2,14,STEEL)
        self.rect(x+17,y+3,9,6,DEEP)
        self.rect(x+17,y+10,9,7,MID)
        self.rect(x+5+variant,y+6,2,2,MID)
        self.path(f'M{x+18} {y+12}h5v2h2v2h-7Z',WHITE)
        self.rect(x+18,y+4,3,3,PALE)
        self.rect(x+24,y+3,2,13,WHITE,.5)
        self.rect(x+4,y+18,18,1,STEEL)


def _coffee(d):
    # Fuji Cafe Mania: bean canisters, touch panel, deep cup recess, drip tray.
    d.body(13,31,61,109,10,INK,DARK,STEEL)
    for x in (17,35,53):
        d.body(x,12,15,21,4,DARK,INK,STEEL)
        d.rect(x+2,15,11,15,DEEP)
        for yy,xx in ((23,3),(25,7),(27,2),(20,8)):
            d.rect(x+xx,yy,3,2,STEEL)
        d.rect(x+2,14,2,13,PALE,.45)
        d.rect(x+1,10,15,3,PALE)
    d.rect(17,35,53,42,STEEL)
    d.rect(19,37,49,38,BLACK)
    d.rect(22,40,43,29,DEEP)
    d.group('screen-response')
    d.text(26,47,'COFFEE',6,PALE)
    for x,y in ((26,52),(41,52),(54,52)):
        d.path(f'M{x} {y}h7v6h-6Z',WHITE)
        d.rect(x+2,y-2,3,1,PALE)
        d.rect(x,y+9,8,2,MINT)
    d.end()
    # Clear volume below the screen is the decisive coffee-machine silhouette.
    d.rect(18,80,51,49,BLACK)
    d.poly([(19,81),(26,85),(26,122),(19,127)],STEEL)
    d.poly([(26,85),(64,85),(68,81),(19,81)],DARK)
    d.rect(27,85,35,35,DARK)
    d.rect(39,80,15,7,STEEL)
    d.rect(42,85,9,5,PALE)
    d.rect(45,90,3,4,BLACK)
    d.poly([(27,119),(63,119),(68,126),(20,126)],STEEL)
    for x in range(25,63,5):d.rect(x,122,2,4,INK)
    d.path('M37 103h20l-3 17H40Z',WHITE)
    d.rect(38,102,19,3,PALE)
    d.rect(42,108,10,6,DEEP)
    d.rect(44,109,6,2,MINT)
    d.group('ambient steam')
    d.path('M43 101v-4h2v-5h-2v-4h2v-3h2v5h-2v4h2v5h-2v2Z',WHITE,.7)
    d.end()
    d.rect(18,132,50,5,DARK)
    d.rect(62,133,4,2,MINT)
    # Small cup-stack and lid recess belong to the adjoining counter.
    d.body(82,113,13,28,3,STEEL,DARK,PALE)
    for y in (109,114,119,124):
        d.path(f'M81 {y}h16l-2 6H83Z',WHITE)
        d.rect(81,y,16,2,PALE)


def _warmer(d):
    d.body(5,17,73,60,10,STEEL,DARK,PALE)
    d.rect(8,20,67,9,PALE)
    d.vent(13,22,14,color=DARK)
    d.rect(9,31,65,38,BLACK)
    d.rect(12,32,59,35,DARK)
    d.poly([(74,31),(83,27),(83,64),(74,69)],DEEP)
    d.group('ambient warmer-light')
    d.rect(14,32,55,3,WHITE)
    d.rect(12,35,59,30,MID,.2)
    d.end()
    for yy in (47,64):
        d.poly([(13,yy),(66,yy),(71,yy+3),(11,yy+3)],STEEL)
        d.rect(12,yy+3,59,2,PALE)
        for xx in range(15,68,6):d.rect(xx,yy,1,3,WHITE)
    # Shallow trays and recognisably different hot-food shapes.
    for x,y,w in ((15,42,20),(39,41,25),(16,59,28),(48,59,17)):
        d.rect(x,y,w,4,PALE);d.rect(x+1,y,w-2,2,STEEL)
    for x,y in ((18,37),(26,36),(20,54),(29,54),(52,53)):
        d.path(f'M{x} {y}h5v2h2v4h-9v-4h2Z',MID)
        d.rect(x+1,y+1,3,2,WHITE)
    for x,y in ((42,36),(51,35)):
        d.path(f'M{x} {y}h8v2h2v3h-12v-3h2Z',PALE)
        d.rect(x+1,y+2,7,1,MID)
    d.rect(9,30,2,40,PALE);d.rect(71,30,3,40,PALE)
    d.rect(41,31,1,38,WHITE,.55)
    d.rect(38,48,2,7,STEEL)
    d.poly([(16,32),(20,32),(39,66),(35,66)],WHITE,.09)
    d.rect(12,72,49,2,MID)
    d.rect(66,72,5,2,MINT)
    d.rect(9,77,6,5,BLACK);d.rect(68,77,6,5,BLACK)


def _checkout(d):
    # Lipped counter: appliances are independent objects on its top surface.
    d.body(4,84,174,48,14,STEEL,DARK,PALE)
    d.poly([(4,84),(18,60),(192,60),(178,84)],PALE)
    d.poly([(10,82),(22,64),(185,64),(174,82)],WHITE)
    d.rect(7,89,167,3,MINT)
    d.rect(11,98,76,27,DARK);d.rect(91,98,76,27,DARK)
    d.rect(15,101,68,2,STEEL);d.rect(95,101,68,2,STEEL)
    d.rect(72,106,8,2,MID);d.rect(98,106,8,2,MID)
    # Monitor tilts away from the customer, with triangular rear support.
    d.poly([(59,27),(71,30),(91,74),(72,76)],STEEL)
    d.poly([(57,31),(65,32),(76,72),(62,72)],DARK)
    d.poly([(32,19),(88,19),(80,60),(24,60)],INK)
    d.poly([(36,23),(83,23),(77,54),(29,54)],STEEL)
    d.poly([(39,26),(79,26),(74,50),(34,50)],DEEP)
    d.group('screen-response')
    d.group('ambient pos-display')
    d.text(42,36,'TOTAL',6,PALE);d.text(40,46,'¥ 057',9,MINT)
    d.end();d.end()
    d.poly([(47,61),(67,61),(73,75),(41,75)],DARK)
    d.poly([(36,72),(75,72),(84,79),(29,79)],STEEL)
    # Keyboard presents a shallow perspective, not another display.
    d.poly([(27,66),(53,66),(48,72),(22,72)],INK)
    for j in range(2):
        for i in range(6):d.rect(27+i*4-j,67+j*2,2,1,PALE)
    # Receipt printer and paper feed.
    d.body(127,52,34,29,8,PALE,STEEL,WHITE)
    d.poly([(130,51),(137,47),(165,47),(158,51)],STEEL)
    d.rect(131,56,25,5,BLACK)
    d.rect(154,65,3,2,MINT)
    d.group('paper-response');d.group('ambient printer')
    d.path('M134 57h19v8h-2v18h-18v-3h2V64h-1Z',WHITE)
    for y,w in ((63,12),(66,9),(69,13),(73,7),(76,12)):
        d.rect(137,y,w,1,STEEL)
    d.end();d.end()
    # Handheld barcode scanner with unmistakable pistol profile, cord and dock.
    d.poly([(103,43),(114,45),(112,55),(108,56),(104,69),(99,67),(102,54),(98,51)],DARK)
    d.poly([(102,44),(112,46),(110,49),(101,48)],MINT)
    d.poly([(97,68),(108,68),(113,74),(94,74)],STEEL)
    d.path('M112 68h5v-9h5v-2h-7v9h-3Z',INK)
    # Customer coin tray, shallow and empty rather than an anonymous green tile.
    d.poly([(78,82),(104,82),(110,87),(74,87)],DARK)
    d.poly([(80,83),(102,83),(105,85),(78,85)],STEEL)
    d.rect(87,83,4,2,PALE)


def _microwave(d):
    d.body(5,25,73,49,10,PALE,STEEL,WHITE)
    d.rect(10,31,48,35,INK)
    d.rect(13,34,40,28,DARK)
    d.rect(16,37,34,22,BLACK)
    # Fine perforated door screen with a dish visible behind it.
    d.path('M22 51h22v6H24Z',STEEL)
    d.rect(21,49,25,2,PALE)
    for y in range(38,59,4):
        for x in range(17,49,4):d.rect(x,y,1,1,MID)
    d.rect(54,38,3,22,WHITE)
    d.rect(62,32,12,9,BLACK)
    d.group('ambient microwave');d.text(63,38,'0:57',4.5,MINT);d.end()
    for y in (45,50,55):
        d.rect(63,y,4,3,STEEL);d.rect(70,y,4,3,STEEL)
    d.rect(64,62,9,4,DARK);d.rect(66,63,5,2,MINT)
    for x in range(12,57,5):d.rect(x,69,3,2,STEEL)
    d.poly([(79,32),(85,29),(85,59),(79,62)],DARK)
    for y in range(35,58,5):d.rect(80,y,4,2,STEEL)
    d.rect(12,74,8,4,BLACK);d.rect(65,74,8,4,BLACK)


def _magazines(d):
    # A low sloping display: staggered face-out covers and thin retaining rails.
    d.poly([(7,146),(84,146),(97,133),(97,22),(86,28),(86,143)],BLACK,.4)
    d.poly([(9,27),(21,17),(94,17),(82,27)],PALE)
    d.poly([(82,27),(94,17),(94,145),(82,155)],STEEL)
    d.rect(9,27,73,128,DARK)
    d.rect(9,27,3,128,PALE)
    d.rect(80,27,3,128,PALE)
    for row,(y,n) in enumerate(((32,3),(69,3),(107,3))):
        d.poly([(14,y+30),(76,y+30),(81,y+37),(11,y+37)],STEEL)
        d.group('stock-response')
        for col in range(n):
            x=15+col*21;yy=y+(2 if col==1 else 0)
            # The visible right page edge makes these thin books, not packages.
            d.poly([(x,yy+2),(x+17,yy),(x+19,yy+28),(x+1,yy+31)],INK)
            d.poly([(x+2,yy+3),(x+16,yy+1),(x+17,yy+26),(x+3,yy+29)],(PALE,MID,WHITE)[(row+col)%3])
            d.poly([(x+17,yy+1),(x+19,yy+2),(x+20,yy+28),(x+18,yy+30)],WHITE)
            d.rect(x+4,yy+5,10,3,DEEP)
            if (row+col)%3==0:
                # Portrait cover: hair, face, coat.
                d.rect(x+7,yy+11,6,7,STEEL);d.rect(x+6,yy+10,8,3,INK)
                d.path(f'M{x+5} {yy+19}h9v2h2v5h-13v-5h2Z',DEEP)
            elif (row+col)%3==1:
                # Graphic cover with a mountain and column.
                d.poly([(x+4,yy+23),(x+10,yy+12),(x+15,yy+23)],DEEP)
                d.rect(x+4,yy+11,3,4,MINT)
            else:
                d.rect(x+4,yy+12,12,6,DEEP)
                d.rect(x+6,yy+13,7,2,PALE)
                for k in range(3):d.rect(x+5,yy+21+k*2,9-k*2,1,STEEL)
        d.end()
        d.rect(12,y+32,68,3,PALE);d.rect(13,y+35,67,2,INK)
    d.rect(9,151,73,5,STEEL)
    d.rect(12,156,7,6,INK);d.rect(74,156,7,6,INK)


def _fresh(d, variant='fresh'):
    d.body(5,17,76,174,12,PALE,STEEL,WHITE)
    d.rect(9,27,68,132,BLACK)
    d.rect(13,30,60,126,DARK)
    d.poly([(77,27),(87,23),(87,151),(77,159)],DEEP)
    d.rect(9,19,68,8,WHITE)
    d.group('ambient case-light')
    d.rect(13,29,60,3,MINT)
    for yy in (59,91,123):d.rect(13,yy,60,2,WHITE)
    d.end()
    d.group('stock-response')
    if variant == 'dairy':
        # Gable-top milk cartons, narrow-neck milk bottles, foil-lid yogurt
        # and pudding cups are deliberately different from prepared meals.
        for xx in (15,35,55):
            d.carton(xx,35,23,WHITE if xx==35 else PALE)
        for index,xx in enumerate((16,31,46,61)):
            d.bottle(xx,67,23,WHITE,index+1)
            d.rect(xx+2,82,7,4,MID)
        for xx in (15,36,57):
            d.path(f'M{xx} 106h17l-2 15H{xx+2}Z',PALE)
            d.path(f'M{xx+1} 103h15l3 3H{xx-1}Z',WHITE)
            d.rect(xx+3,109,11,8,DEEP)
            d.rect(xx+5,111,7,2,WHITE)
            d.rect(xx+2,106,2,12,WHITE)
        for index,xx in enumerate((15,36,57)):
            d.path(f'M{xx+1} 137h16l-3 15H{xx+4}Z',MID)
            d.rect(xx+4,140,10,7,PALE)
            d.rect(xx+5,141,8,2,WHITE)
            d.path(f'M{xx+1} 134h16l2 3H{xx-1}Z',WHITE)
            d.rect(xx+4,134,10,2,DEEP if index%2 else STEEL)
            d.rect(xx+1,137,2,10,WHITE)
    elif variant == 'bento':
        # Compartmented bento trays occupy the upper shelves.
        d.bento(14,37,0);d.bento(45,37,2)
        d.bento(14,69,2);d.bento(45,69,0)
        # Wide, shallow pasta box with visible strands, sauce and clear lid.
        d.path('M16 102h53l3 3v15l-3 2H16l-3-2v-15Z',INK)
        d.rect(16,105,53,14,PALE)
        for xx in (20,29,38,47,56):
            d.path(f'M{xx} 108h7v2h-5v3h6v2h-8v-5h5v-2Z',WHITE)
        d.rect(58,107,7,9,MID);d.rect(60,109,3,3,DEEP)
        d.rect(17,103,50,1,WHITE);d.rect(68,106,1,12,WHITE)
        # Three transparent salad bowls with stepped lids and leafy contents.
        for xx in (15,36,57):
            d.path(f'M{xx} 139h17l-3 13H{xx+3}Z',PALE)
            d.path(f'M{xx+2} 140h13l-2 9H{xx+4}Z',MID)
            d.rect(xx+4,141,4,4,DEEP);d.rect(xx+10,143,3,4,DEEP)
            d.rect(xx+7,145,3,3,WHITE)
            d.path(f'M{xx+1} 136h15l3 3H{xx-1}Z',WHITE)
            d.rect(xx+2,138,13,1,STEEL)
    else:
        d.rice(15,37);d.rice(37,35,True);d.sandwich(54,36)
        d.sandwich(15,68);d.sandwich(36,69);d.rice(57,69,True)
        d.rice(15,101,True);d.sandwich(36,101);d.rice(57,101)
        d.sandwich(15,132);d.rice(37,133);d.sandwich(55,132)
    d.end()
    for yy in (60,92,124,155):
        d.poly([(12,yy),(72,yy),(77,yy+4),(9,yy+4)],STEEL)
        d.rect(9,yy+4,68,3,PALE)
        for xx in (17,39,61):d.label(xx,yy+4,9,WHITE)
    # Air return grille lives below the open display, not across its food.
    d.rect(10,168,65,17,DARK)
    for y in (170,175,180):
        for x in range(13,72,6):d.rect(x,y,4,2,STEEL)
    d.rect(66,161,8,4,INK);d.rect(68,162,4,1,MINT)
    d.group('ambient glass-light')
    d.poly([(79,31),(82,30),(82,148),(79,151)],WHITE,.25)
    d.end()


def _freezer(d):
    # A top-opening low chest with deep, divided bins, not a front-opening box.
    d.body(5,45,105,47,10,PALE,STEEL,WHITE)
    d.poly([(5,45),(16,15),(119,15),(110,45)],STEEL)
    d.poly([(10,43),(19,19),(113,19),(106,43)],BLACK)
    d.poly([(14,41),(21,22),(109,22),(102,41)],DARK)
    # Basket divisions and visible ice-cream packages beneath the sliding lids.
    for x in (20,43,66,89):
        d.poly([(x,39),(x+6,24),(x+23,24),(x+18,39)],MID)
        for j in range(4):d.rect(x+5+j*4,29,1,9,PALE)
    for x,y in ((23,28),(32,32),(47,27),(61,32),(75,27),(93,30)):
        d.path(f'M{x} {y}h7v2h1v7h-9v-7h1Z',WHITE if x%2 else MID)
        d.rect(x+2,y+3,4,3,DEEP)
    d.rect(83,30,8,8,PALE);d.rect(82,29,10,2,WHITE)
    d.group('ambient freezer-light')
    d.path('M18 24h2l-5 15h-2Z',MINT)
    d.rect(20,20,90,2,WHITE)
    d.end()
    # Two panes travel front/back; central rail and separate handles clarify it.
    d.poly([(11,42),(19,19),(64,19),(56,42)],PALE,.13)
    d.poly([(58,42),(66,19),(113,19),(105,42)],PALE,.12)
    d.path('M62 19h3l-8 23h-3Z',PALE)
    d.rect(14,40,91,2,PALE)
    d.poly([(32,35),(41,35),(43,38),(31,38)],STEEL)
    d.rect(33,34,7,2,WHITE)
    d.poly([(80,26),(89,26),(91,29),(79,29)],STEEL)
    d.rect(81,25,7,2,WHITE)
    d.group('ambient freezer-reflection reflection')
    d.poly([(29,22),(34,22),(26,37),(21,37)],WHITE,.3)
    d.poly([(91,21),(94,21),(87,38),(84,38)],WHITE,.2)
    d.end()
    d.rect(10,51,95,3,MID);d.rect(10,82,95,2,MID)
    d.rect(82,61,22,17,STEEL)
    d.rect(85,63,14,4,INK);d.text(87,66,'-20',3.5,MINT)
    for yy in (70,73):d.rect(85,yy,15,1,DARK)
    d.rect(14,92,6,5,BLACK);d.rect(99,92,6,5,BLACK)


def _drinks(d):
    d.body(5,15,293,119,13,STEEL,DARK,PALE)
    d.rect(10,18,284,8,DARK)
    d.rect(14,20,277,2,PALE)
    for bay in range(3):
        x=13+94*bay
        d.rect(x,29,89,94,INK)
        d.rect(x+4,33,81,84,DEEP)
        d.group('ambient drinks-light')
        d.rect(x+4,33,2,83,MINT)
        d.rect(x+7,33,75,2,WHITE)
        d.rect(x+7,35,75,80,MINT,.04)
        d.end()
        for row in range(3):
            yy=37+row*27
            # Mixed silhouettes, broken spacing, different fill levels/labels.
            cursor=x+10
            for col in range(5):
                variant=(row+col+bay)%5
                if variant==0:
                    d.carton(cursor,yy+1,22,PALE);cursor+=16
                elif variant==1:
                    d.can(cursor,yy+7,15,WHITE);cursor+=14
                else:
                    height=22 if variant==2 else 20
                    d.bottle(cursor,yy+22-height,height,(MID,PALE,MINT)[(col+bay)%3],variant)
                    cursor+=14 if variant==2 else 13
            d.rect(x+4,yy+24,81,2,PALE)
            for xx in (x+12,x+39,x+66):d.label(xx,yy+24,11)
        # Narrow door frame with edge-mounted pull, not a screen bezel.
        d.rect(x+1,29,2,94,PALE);d.rect(x+86,29,2,94,PALE)
        d.rect(x+83,58,3,27,INK);d.rect(x+84,59,2,23,WHITE)
        d.group('ambient drink-reflection reflection')
        d.poly([(x+12,36),(x+18,36),(x+63,114),(x+57,114)],WHITE,.09)
        d.poly([(x+63,36),(x+66,36),(x+81,61),(x+81,68)],WHITE,.08)
        d.end()
    d.rect(10,126,283,4,DARK)
    d.vent(16,127,66,color=STEEL)
    d.rect(270,19,18,5,BLACK);d.text(274,23,'4°C',4,MINT)
    d.rect(17,135,8,4,BLACK);d.rect(282,135,8,4,BLACK)


_EQUIPMENT = {
    'coffee': (104,150,_coffee),
    'warmer': (96,88,_warmer),
    'checkout': (200,145,_checkout),
    'microwave': (96,88,_microwave),
    'magazines': (104,165,_magazines),
    'fresh': (104,200,_fresh),
    'bento': (104,200,lambda d: _fresh(d, 'bento')),
    'dairy': (104,200,lambda d: _fresh(d, 'dairy')),
    'freezer': (126,102,_freezer),
    'drinks': (318,146,_drinks),
}


def render_equipment(kind, x, y, w, h):
    """Return self-contained SVG markup suitable for embedding in scene SVG.

    Native aspect ratio is retained inside the supplied bounds. All identifiers
    are classes, so multiple instances can be embedded without duplicate IDs.
    """
    if kind not in _EQUIPMENT:
        raise ValueError(f'Unknown equipment kind: {kind}')
    if w <= 0 or h <= 0:
        raise ValueError('Equipment bounds must be positive')
    vw,vh,draw = _EQUIPMENT[kind]
    drawing = Drawing()
    draw(drawing)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" '
            f'viewBox="0 0 {vw} {vh}" preserveAspectRatio="xMidYMax meet" '
            f'class="equipment equipment-{kind}" overflow="visible" '
            'shape-rendering="crispEdges" aria-hidden="true">'
            + ''.join(drawing.parts) + '</svg>')
