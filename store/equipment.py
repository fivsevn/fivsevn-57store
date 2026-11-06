"""Code-drawn equipment in a single high-angle, north-up projection.

X stays horizontal; floor depth runs down the page; height projects only up.
The visible south fascia is short (roughly 10–18% of each footprint). The art
shows upper surfaces and opened display interiors, never full front elevations.
No images, external assets, gradients or filters are used.
"""
from html import escape

INK='#101b1a'; BLACK='#091210'; DARK='#20312e'; DEEP='#304d40'
STEEL='#647e74'; MID='#8ba78d'; PALE='#bdcdc0'; WHITE='#e0e8d7'; MINT='#50efc2'


class Drawing:
    def __init__(self): self.parts=[]

    def rect(self,x,y,w,h,color,opacity=None):
        if w<=0 or h<=0:return
        op='' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"{op}/>')

    def path(self,d,color,opacity=None):
        op='' if opacity is None else f' opacity="{opacity}"'
        self.parts.append(f'<path d="{d}" fill="{color}"{op}/>')

    def poly(self,pts,color,opacity=None):
        self.path('M'+' '.join(f'{x},{y}' for x,y in pts)+'Z',color,opacity)

    def group(self,classes='',transform=''):
        cls=f' class="{classes}"' if classes else ''
        tr=f' transform="{transform}"' if transform else ''
        self.parts.append(f'<g{cls}{tr}>')

    def end(self):self.parts.append('</g>')

    def text(self,x,y,value,size=6,color=MINT):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="monospace" font-size="{size}">{escape(value)}</text>')

    def body(self,x,y,w,depth,front=10,color=PALE,fascia=STEEL):
        """An overhead rectangle with one short south face; no right face."""
        self.rect(x+2,y+depth+front,w,4,BLACK,.45)
        self.rect(x,y,w,depth+front,INK)
        self.rect(x+2,y+2,w-4,depth-2,color)
        self.rect(x+2,y+depth,w-4,front-2,fascia)
        self.rect(x+2,y+2,w-4,2,WHITE)
        self.rect(x+2,y+depth-2,w-4,2,PALE)
        self.rect(x+2,y+2,2,depth-2,PALE)
        self.rect(x+w-4,y+4,2,depth-4,STEEL)

    def vent(self,x,y,cols,rows=1,color=INK,step=4):
        for j in range(rows):
            for i in range(cols):self.rect(x+i*step,y+j*4,2,2,color)

    def label(self,x,y,w,color=WHITE):
        self.rect(x,y,w,3,color);self.rect(x+1,y+1,max(1,w-3),1,STEEL)

    def round(self,x,y,w,h,color):
        # Stepped octagon; a readable top rim without smooth vector circles.
        c=min(3,w//3,h//3)
        self.path(f'M{x+c} {y}H{x+w-c}v1h{c-1}v{c-1}h1V{y+h-c}h-1v{c-1}h{1-c}v1H{x+c}v-1h{1-c}v{1-c}h-1V{y+c}h1v{1-c}h{c-1}Z',color)

    def bottle(self,x,y,color=MID,kind=0):
        # From above the shoulder and cap dominate; only a tiny south side shows.
        self.round(x,y+2,13,17,INK)
        self.round(x+1,y,11,16,color)
        self.rect(x+3,y+1,6,2,PALE)
        self.round(x+3,y+2,6,7,WHITE if kind%2 else STEEL)
        self.rect(x+5,y+4,2,3,DEEP)
        self.rect(x+3,y+11,6,3,WHITE if kind%3 else DEEP)
        self.rect(x+4,y+12,4,1,STEEL)

    def can(self,x,y,color=PALE):
        self.round(x,y+2,12,15,STEEL)
        self.round(x,y,12,13,color)
        self.round(x+2,y+2,8,8,WHITE)
        self.rect(x+5,y+3,3,4,STEEL);self.rect(x+6,y+4,1,2,INK)
        self.rect(x+3,y+11,6,2,DEEP)

    def carton(self,x,y,color=PALE):
        self.rect(x,y+2,14,19,STEEL)
        self.rect(x,y,14,17,color)
        self.poly([(x,y+6),(x+7,y),(x+14,y+6)],WHITE)
        self.poly([(x,y+6),(x+7,y+12),(x+14,y+6)],MID)
        self.rect(x+6,y,2,12,PALE)
        self.rect(x+2,y+14,10,3,DEEP)
        self.rect(x+4,y+15,6,1,WHITE)

    def rice(self,x,y,flip=False):
        self.path(f'M{x} {y+16}v-3h2v-3h2v-3h2V{y+4}h2V{y+2}h4v2h2v3h2v3h2v3h2v3Z',STEEL)
        self.path(f'M{x+1} {y+13}v-3h2V{y+7}h3V{y+4}h2V{y+1}h4v3h2v3h3v3h2v3Z',WHITE)
        self.rect(x+(7 if flip else 6),y+8,7,7,DEEP)
        self.rect(x+8,y+9,2,4,INK)
        self.rect(x+9,y+2,3,2,MID)
        self.rect(x+1,y+17,18,2,PALE)

    def sandwich(self,x,y):
        self.rect(x,y+1,22,19,STEEL)
        self.rect(x+1,y,20,17,PALE)
        self.poly([(x+3,y+14),(x+18,y+2),(x+18,y+14)],WHITE)
        self.poly([(x+6,y+14),(x+18,y+5),(x+18,y+8),(x+10,y+14)],MID)
        self.poly([(x+11,y+14),(x+18,y+9),(x+18,y+11),(x+14,y+14)],DEEP)
        self.rect(x+2,y+1,5,3,WHITE)
        self.rect(x+2,y+17,18,1,WHITE)

    def bento(self,x,y,variant=0):
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

    def cup(self,x,y,color=PALE):
        self.round(x,y+3,17,17,STEEL)
        self.round(x,y,17,17,color)
        self.round(x+2,y+2,13,13,WHITE)
        self.round(x+4,y+4,9,9,DEEP)
        self.rect(x+5,y+5,4,2,MID)


def _coffee(d):
    # Its rectangular lid and three bean hoppers are seen from overhead.
    d.body(8,9,70,119,14,DARK,INK)
    d.rect(13,14,60,73,STEEL)
    d.rect(16,17,54,65,DARK)
    for index,x in enumerate((18,35,52)):
        d.rect(x,20,15,40,INK);d.rect(x+2,22,11,35,DEEP)
        for k in range(7):
            xx=x+3+(k*3+index)%7;yy=27+(k*7)%26
            d.path(f'M{xx} {yy}h3v1h1v2h-4Z',MID if k%2 else STEEL)
            d.rect(xx+1,yy,1,2,INK)
        d.rect(x+2,22,11,2,PALE);d.rect(x+2,24,2,29,PALE,.35)
        d.rect(x+5,53,6,2,WHITE,.25)
    d.rect(18,64,49,3,INK)
    d.vent(21,69,11,color=INK)
    # Sloping control strip is compressed against the front of the housing.
    d.rect(17,77,52,12,INK);d.rect(20,79,46,7,DEEP)
    d.group('screen-response')
    for xx in (24,39,54):
        d.rect(xx,80,7,3,PALE);d.rect(xx,84,7,1,MINT)
    d.end()
    # Cup recess and drip tray are an open plan area, not a tall black window.
    d.rect(14,91,58,33,BLACK)
    d.rect(18,95,50,25,STEEL)
    for xx in range(21,67,5):d.rect(xx,97,2,21,INK)
    d.rect(37,88,15,9,PALE);d.rect(42,94,5,5,INK)
    d.cup(36,101,WHITE)
    d.group('ambient steam')
    d.path('M43 107v-4h2v-4h-2v-4h2v-3h2v5h-2v4h2v4h-2v2Z',WHITE,.7)
    d.end()
    d.rect(14,131,52,3,STEEL);d.rect(65,134,4,2,MINT)
    # Two stacks of empty cups expose circular openings.
    for yy in (99,119):
        d.round(82,yy+4,17,18,STEEL)
        d.round(82,yy,17,17,WHITE)
        d.round(85,yy+3,11,11,INK)
        d.round(87,yy+5,7,7,PALE)


def _warmer(d):
    # Glass canopy seen from above, with metal trays visible through its roof.
    d.body(5,6,86,66,10,STEEL,DARK)
    d.rect(10,11,76,56,INK);d.rect(13,15,70,47,DEEP)
    d.group('ambient warmer-light')
    d.rect(13,13,70,3,WHITE);d.rect(13,16,70,45,MID,.18)
    d.end()
    for x,y,w,h in ((17,20,27,17),(49,20,29,17),(17,42,27,16),(49,42,29,16)):
        d.rect(x,y,w,h,PALE);d.rect(x+2,y+2,w-4,h-4,STEEL)
        d.rect(x+2,y+2,w-4,1,WHITE)
    for x,y in ((21,24),(32,25),(21,46),(31,48),(55,46),(66,47)):
        d.path(f'M{x+2} {y}h4v2h3v4h-2v2h-6v-2h-2v-4h3Z',MID)
        d.rect(x+3,y+2,3,2,WHITE)
    for y in (24,31):
        d.path(f'M54 {y}h19v2h2v2H52v-2h2Z',PALE)
        d.rect(57,y+1,12,1,MID)
    # The thin rails belong to the canopy; no full-height front windows.
    d.rect(11,12,2,53,PALE);d.rect(83,12,2,53,PALE)
    d.rect(46,14,2,48,PALE,.65)
    d.poly([(18,17),(23,17),(41,60),(36,60)],WHITE,.1)
    d.rect(12,65,72,3,PALE)
    d.vent(13,75,14,color=STEEL)
    d.rect(77,75,5,2,MINT)


def _checkout(d):
    # Counter worktop fills the footprint. A short south fascia is all we see.
    d.body(5,10,190,115,14,PALE,STEEL)
    d.rect(10,15,180,105,WHITE)
    d.rect(11,118,178,3,PALE)
    d.rect(10,128,180,3,MINT)
    d.rect(13,134,82,2,DARK);d.rect(101,134,83,2,DARK)
    # POS: back shell, a shallow tilted screen, base and keyboard on the desk.
    d.rect(24,25,60,33,DARK)
    d.rect(28,27,52,23,INK)
    d.rect(31,30,46,16,DEEP)
    d.group('screen-response');d.group('ambient pos-display')
    d.text(35,36,'TOTAL',5,PALE);d.text(34,43,'¥ 057',6,MINT)
    d.end();d.end()
    d.rect(48,52,12,11,STEEL)
    d.rect(37,60,35,8,INK);d.rect(40,61,29,3,STEEL)
    d.rect(23,73,59,20,DARK);d.rect(25,75,55,15,STEEL)
    for yy in (77,81,85):
        for xx in range(28,76,7):d.rect(xx,yy,5,2,PALE)
    d.rect(43,88,25,2,PALE)
    # Small printer's lid is much larger than its visible front edge.
    d.body(135,30,42,39,6,PALE,STEEL)
    d.rect(140,35,32,24,WHITE)
    d.rect(142,38,28,2,STEEL);d.rect(142,41,28,1,MID)
    d.rect(141,61,29,4,BLACK);d.rect(169,65,3,2,MINT)
    d.group('paper-response');d.group('ambient printer')
    d.path('M145 62h21v23h-2v15h-22v-3h2V78h1Z',WHITE)
    for yy,ww in ((68,15),(72,12),(76,16),(81,9),(86,15),(91,12)):
        d.rect(147,yy,ww,1,STEEL)
    d.end();d.end()
    # Scanner lying in its cradle, top light and cable visible.
    d.rect(98,66,21,16,STEEL)
    d.path('M95 40h24v17h-7v19h-9V57h-8Z',INK)
    d.rect(98,43,18,7,DEEP);d.rect(99,43,16,2,MINT)
    d.rect(105,58,5,15,STEEL)
    d.path('M111 75h12v-18h6v-2h-8v18h-10Z',DARK)
    # Long customer coin tray, laid flat on the south edge.
    d.rect(76,106,42,10,STEEL);d.rect(79,108,36,6,DEEP)
    d.round(85,108,7,6,PALE);d.rect(99,109,10,3,MID)


def _microwave(d):
    d.body(5,7,86,59,15,PALE,STEEL)
    # Broad metal top with seams, shallow pressed panel and rear ventilation.
    d.rect(11,12,74,46,WHITE)
    d.rect(16,17,64,35,PALE);d.rect(18,19,60,31,WHITE)
    d.rect(20,47,56,1,PALE)
    for yy in (17,21,25):d.rect(62,yy,14,2,STEEL)
    d.rect(13,12,2,44,MID);d.rect(82,13,1,43,STEEL)
    # Compressed south door and control strip are secondary to the lid.
    d.rect(10,68,53,10,INK);d.rect(13,70,44,6,DARK)
    for yy in (71,74):
        for xx in range(16,55,4):d.rect(xx,yy,1,1,MID)
    d.rect(59,70,3,6,WHITE)
    d.rect(67,68,18,6,BLACK)
    d.group('ambient microwave');d.text(70,73,'0:57',4,MINT);d.end()
    d.rect(69,76,4,2,PALE);d.rect(77,76,6,2,MINT)


def _magazines(d):
    # This wall fixture faces WEST. Its east spine is raised; shallow trays
    # slope left into the public aisle. The south face is just an end board.
    d.body(6,10,91,135,11,DARK,STEEL)
    d.rect(83,15,10,126,PALE)
    d.rect(85,18,5,120,STEEL)
    d.rect(80,17,3,122,INK)
    for yy in (18,58,98):
        d.rect(12,yy,69,38,STEEL)
        d.rect(15,yy+2,63,33,DEEP)
        d.rect(15,yy+2,3,33,MID)
        d.rect(75,yy+2,3,33,INK)
        # Sideways covers expose their front edge to the west-facing aisle.
        d.group('stock-response')
        for col in range(2):
            x=17+col*30;y=yy+4+(col%2)
            d.group(transform=f'translate({x+28} {y}) rotate(90)')
            d.rect(1,2,25,28,WHITE);d.rect(2,28,23,1,STEEL)
            d.rect(0,0,24,27,(PALE,MID,WHITE)[(yy//40+col)%3])
            d.rect(3,3,17,3,DEEP)
            variant=(yy//40+col)%3
            if variant==0:
                d.rect(9,10,7,7,STEEL);d.rect(8,9,9,3,INK)
                d.path('M6 18h13v7H4v-5h2Z',DEEP)
            elif variant==1:
                d.poly([(4,24),(12,10),(20,24)],DEEP)
                d.rect(3,10,4,4,MINT)
            else:
                d.rect(4,10,16,6,DEEP);d.rect(7,12,10,2,PALE)
                for k in range(3):d.rect(4,20+k*2,14-k*2,1,STEEL)
            d.rect(0,0,1,26,PALE)
            d.end()
        d.end()
        # The retaining lip is on the aisle edge, not at the south of each row.
        d.rect(10,yy+2,3,34,PALE)
        d.rect(13,yy+3,1,32,INK)
    d.rect(11,147,81,2,PALE)
    d.rect(12,151,79,1,DARK)


def _fresh(d,variant='fresh'):
    # The camera is shared, but the fixtures follow their walls. Fresh/bento
    # back onto the east wall and open west; dairy backs west and opens east.
    east_open=variant=='dairy'
    back_x=11 if east_open else 82
    deck_x=29 if east_open else 11
    open_x=90 if east_open else 10
    d.body(6,8,91,166,13,PALE,STEEL)
    # A long insulated spine and refrigeration duct run beside the wall.
    d.rect(back_x,14,13,154,STEEL)
    d.rect(back_x+2,17,9,148,PALE)
    for yy in range(24,158,7):
        d.rect(back_x+4,yy,5,2,DARK)
    d.rect(back_x+(12 if east_open else 0),14,2,154,INK)
    d.rect(deck_x,16,63,152,INK)
    d.rect(deck_x+3,19,57,146,DEEP)
    d.group('ambient case-light')
    d.rect(back_x+(14 if east_open else -2),19,2,145,MINT)
    d.rect(open_x,20,2,143,WHITE)
    d.end()
    # Each shallow merchandise lane extends from the wall towards the aisle.
    for yy in (22,59,96,133):
        d.rect(deck_x+2,yy,59,32,STEEL)
        d.rect(deck_x+4,yy+2,55,27,DARK)
        d.rect(deck_x+3,yy+29,57,2,PALE)
        d.rect(open_x,yy+2,3,27,MID)
        d.rect(open_x,yy+9,4,11,WHITE)
        d.rect(open_x+1,yy+11,1,6,STEEL)

    def merchandise(fn,x,y,width,height,*args):
        # Package fronts also face the aisle rather than every cover facing down.
        tr=(f'translate({x} {y+width}) rotate(-90)' if east_open else
            f'translate({x+height} {y}) rotate(90)')
        d.group(transform=tr);fn(0,0,*args);d.end()

    d.group('stock-response')
    if variant=='bento':
        for row,yy in enumerate((23,60,97)):
            merchandise(d.bento,18,yy,29,21,row%2)
            merchandise(d.bento,48,yy,29,21,(row+1)%2)
        # Open pasta tray and a leafy salad bowl viewed through flat lids.
        d.rect(18,137,27,23,INK);d.rect(20,139,23,18,PALE)
        for xx in (23,31):
            d.path(f'M{xx} 142h7v2h-5v3h6v2h-8v-5h5v-2Z',WHITE)
        d.cup(51,138,MID);d.rect(57,144,4,4,PALE)
    elif variant=='dairy':
        for xx in (34,62):merchandise(d.carton,xx,26,14,21,WHITE)
        for row,yy in enumerate((64,101)):
            for col,xx in enumerate((35,63)):
                merchandise(d.bottle,xx,yy,13,19,WHITE,row+col)
        for xx in (36,64):d.cup(xx,139,PALE)
    else:
        for row,yy in enumerate((27,64,101,138)):
            merchandise(d.rice,17,yy,20,19,row%2==0)
            if row%2:
                merchandise(d.rice,49,yy,20,19,True)
            else:
                merchandise(d.sandwich,48,yy,22,20)
    d.end()
    # South is a plain end panel, not a customer-facing door or vent bank.
    d.rect(12,176,78,2,MID)
    d.rect(back_x+2,156,9,6,INK)
    d.text(back_x+3,160,'4°',3,MINT)
    d.group('ambient glass-light')
    d.rect(open_x+1,22,1,140,WHITE,.35)
    d.end()


def _freezer(d):
    # Overhead sliding glass lids and deep wire baskets occupy almost all of it.
    d.body(5,7,116,76,12,PALE,STEEL)
    d.rect(11,13,104,64,INK);d.rect(15,17,96,56,DARK)
    for x,y in ((18,20),(64,20),(18,47),(64,47)):
        d.rect(x,y,42,23,MID);d.rect(x+2,y+2,38,19,DEEP)
        for xx in range(x+3,x+40,6):d.rect(xx,y+2,1,19,PALE)
        for yy in (y+6,y+13,y+19):d.rect(x+2,yy,38,1,STEEL)
    for x,y in ((22,24),(37,26),(68,23),(86,27),(25,51),(42,52),(69,52)):
        d.path(f'M{x+2} {y}h9v2h2v11h-2v2h-9v-2h-2V{y+2}h2Z',WHITE if x%2 else PALE)
        d.rect(x+3,y+4,7,6,DEEP);d.rect(x+4,y+5,5,2,MID)
    d.cup(87,50,PALE)
    d.group('ambient freezer-light')
    d.rect(13,18,2,54,MINT);d.rect(16,15,94,2,WHITE)
    d.end()
    d.rect(15,17,46,55,PALE,.09);d.rect(63,17,47,55,PALE,.13)
    d.rect(60,14,3,61,PALE)
    d.rect(16,43,93,2,STEEL)
    d.rect(32,61,14,4,STEEL);d.rect(34,60,10,2,WHITE)
    d.rect(80,24,14,4,STEEL);d.rect(82,23,10,2,WHITE)
    d.group('ambient freezer-reflection reflection')
    d.poly([(22,20),(28,20),(46,68),(40,68)],WHITE,.2)
    d.poly([(81,19),(84,19),(104,69),(101,69)],WHITE,.18)
    d.end()
    d.rect(11,86,102,2,MID)
    d.rect(91,89,21,4,INK);d.text(96,92,'-20',3.5,MINT)


def _drinks(d):
    # Customers approach from NORTH; the walk-in replenishment room is SOUTH.
    # The roof is cut away to expose deep product lanes. The south-facing short
    # elevation is the insulated rear casing, never the customer glass doors.
    d.body(5,8,307,115,15,STEEL,DARK)
    d.rect(11,108,295,14,PALE)
    for x in range(17,301,6):d.rect(x,114,3,4,DARK)
    for bay in range(3):
        x=13+98*bay
        d.rect(x,25,94,82,INK);d.rect(x+4,29,86,74,DEEP)
        # North glazing is seen edge-on. Each door has its own pull and rail.
        d.rect(x+1,15,92,8,PALE)
        d.rect(x+4,17,86,4,DEEP)
        d.rect(x+70,17,16,2,WHITE)
        d.rect(x+2,23,90,2,STEEL)
        d.group('ambient drinks-light')
        d.rect(x+3,29,2,74,MINT);d.rect(x+6,28,81,2,WHITE)
        d.rect(x+6,30,80,72,MINT,.035)
        d.end()
        for row in range(3):
            yy=32+row*24
            for col in range(5):
                xx=x+9+col*16;variant=(row+col+bay)%5
                if variant==0:d.carton(xx,yy,PALE)
                elif variant==1:d.can(xx,yy+3,WHITE)
                else:d.bottle(xx,yy+2,(MID,PALE,MINT)[(col+bay)%3],variant)
            d.rect(x+5,yy+22,84,1,STEEL)
        d.group('ambient drink-reflection reflection')
        d.rect(x+8,18,35,1,WHITE,.45)
        d.end()
    # Rear access panels face the cold room; plain metal, small service vents.
    for xx in (15,113,211):
        d.rect(xx,126,88,8,STEEL)
        d.rect(xx+3,128,82,1,MID)
        d.rect(xx+66,130,14,2,INK)
    d.rect(276,126,25,7,BLACK);d.text(281,131,'4°C',4,MINT)


_EQUIPMENT={
    'coffee':(104,150,_coffee),
    'warmer':(96,88,_warmer),
    'checkout':(200,145,_checkout),
    'microwave':(96,88,_microwave),
    'magazines':(104,165,_magazines),
    'fresh':(104,200,_fresh),
    'bento':(104,200,lambda d:_fresh(d,'bento')),
    'dairy':(104,200,lambda d:_fresh(d,'dairy')),
    'freezer':(126,102,_freezer),
    'drinks':(318,146,_drinks),
}


def render_equipment(kind,x,y,w,h):
    """Return reusable SVG, preserving native ratio inside the given bounds."""
    if kind not in _EQUIPMENT:raise ValueError(f'Unknown equipment kind: {kind}')
    if w<=0 or h<=0:raise ValueError('Equipment bounds must be positive')
    vw,vh,draw=_EQUIPMENT[kind]
    drawing=Drawing();draw(drawing)
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" '
            f'viewBox="0 0 {vw} {vh}" preserveAspectRatio="xMidYMax meet" '
            f'class="equipment equipment-{kind}" overflow="visible" '
            'shape-rendering="crispEdges" aria-hidden="true">'
            +''.join(drawing.parts)+'</svg>')
