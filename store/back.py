"""Back-room fixtures and people, drawn afresh as metre-scale solid geometry.

All operating faces point along local +Y. Local origins are northwest corners.
References inspected while modelling: TOTO's PureRest QR 2018 release photos
and EIZO's T966 manual front/rear/side drawings. No source pictures are shipped.
"""
from math import sin, cos, pi


FOOTPRINTS = {
    'sys_desk': (1.65, 1.45, 1.38), 'cctv_desk': (1.65, 1.45, 1.38),
    'toilet': (.8, 1.1, 1.05), 'wall_basin': (.65, .5, 1.1),
    'stockrack': (1.4, .55, 1.75), 'lockers': (1., .5, 1.9),
    'utility': (.9, .7, 1.15), 'tea_counter': (1.1, .55, 1.5),
    'cart': (.8, .55, .9), 'stool': (.45, .45, .6),
    'baskets': (.55, .45, .45), 'umbrella': (.55, .45, 1.05),
    'human': (.45, .4, 1.65),
}


def _front(m, x, y, z, w, h, color, **kw):
    m.quad([(x,y,z),(x,y,z+h),(x+w,y,z+h),(x+w,y,z)], color, **kw)


def _top(m, x, y, z, w, d, color, **kw):
    m.quad([(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z)], color, **kw)


def _oval(cx, cy, rx, ry, z, n=12):
    return [(cx+rx*cos(2*pi*i/n), cy+ry*sin(2*pi*i/n), z) for i in range(n)]


def _loft(m, rings, color='paper', cap=True):
    """Stacked oval profiles; useful for real ceramic rather than boxes."""
    for low, high in zip(rings, rings[1:]):
        for i in range(len(low)):
            j=(i+1)%len(low)
            m.quad([low[i],low[j],high[j],high[i]],
                   color if i < len(low)/2 else 'mid', outline=True)
    if cap:
        m.quad(rings[-1], 'white' if color == 'paper' else color, outline=True)


def _oval_ring(m,cx,cy,rx,ry,ix,iy,z,h,color='white',n=12):
    outer0=_oval(cx,cy,rx,ry,z,n); outer=_oval(cx,cy,rx,ry,z+h,n)
    inner0=_oval(cx,cy,ix,iy,z,n); inner=_oval(cx,cy,ix,iy,z+h,n)
    for i in range(n):
        j=(i+1)%n
        m.quad([outer[i],outer[j],inner[j],inner[i]],color,outline=False)
        m.quad([outer0[i],outer0[j],outer[j],outer[i]],'paper',outline=True)
        m.quad([inner0[j],inner0[i],inner[i],inner[j]],'steel',outline=False)


def _bar(m,a,b,r,color='steel',n=6):
    """A slender solid between two 3D endpoints, for pipes and chair braces."""
    dx,dy,dz=(b[i]-a[i] for i in range(3))
    length=(dx*dx+dy*dy+dz*dz)**.5
    if not length:return
    t=(dx/length,dy/length,dz/length)
    seed=(0,0,1) if abs(t[2]) < .9 else (1,0,0)
    u=(t[1]*seed[2]-t[2]*seed[1],t[2]*seed[0]-t[0]*seed[2],t[0]*seed[1]-t[1]*seed[0])
    ul=sum(v*v for v in u)**.5;u=tuple(v/ul for v in u)
    v=(t[1]*u[2]-t[2]*u[1],t[2]*u[0]-t[0]*u[2],t[0]*u[1]-t[1]*u[0])
    rings=[]
    for p in (a,b):
        rings.append([tuple(p[k]+r*(u[k]*cos(2*pi*i/n)+v[k]*sin(2*pi*i/n)) for k in range(3)) for i in range(n)])
    for i in range(n):
        j=(i+1)%n
        m.quad([rings[0][i],rings[0][j],rings[1][j],rings[1][i]],color,outline=False)
    m.quad(rings[1],color,double=True)


def _carton(m,x,y,z,w,d,h,label=True):
    m.box(x,y,z,w,d,h,'mid',top='paper')
    # Fold seams and neutral packing tape; no arbitrary text texture.
    _top(m,x+w*.46,y,z+h+.001,w*.08,d,'mid')
    _front(m,x+w*.46,y+d+.002,z,w*.08,h,'steel')
    if label:
        _front(m,x+w*.12,y+d+.004,z+h*.37,w*.28,h*.27,'paper')
        for j in range(3):
            _front(m,x+w*.16+j*w*.055,y+d+.006,z+h*.41,w*.02,h*.16,'steel')


def _crate(m,x,y,z,w,d,h):
    m.box(x,y,z,w,d,.045,'dark')
    for xx in (x,x+w-.035):
        for yy in (y,y+d-.035):m.box(xx,yy,z,.035,.035,h,'steel')
    for k in range(3):
        zz=z+.06+k*(h-.1)/3
        m.box(x,y,zz,w,.027,.035,'steel')
        m.box(x,y+d-.027,zz,w,.027,.035,'steel')
        m.box(x,y,zz,.027,d,.035,'steel')
        m.box(x+w-.027,y,zz,.027,d,.035,'steel')
    m.box(x,y,z+h-.04,w,d,.04,'mid')
    _top(m,x+.04,y+.04,z+h+.001,w-.08,d-.08,'dark')


def _drawer(m,x,y,z,w,h):
    m=m.part('drawer-front')
    _front(m,x,y,z,w,h,'mid',outline=True)
    m.box(x+w*.35,y+.006,z+h*.69,w*.3,.026,.018,'dark')


def _crt(m,x,y,z,w=.64,depth=.43,h=.46,cctv=False):
    m=m.part('crt-housing')
    # Deep tube housing narrows toward the rear, unlike a flat display.
    front=y+depth
    a=[(x+.08,y,z+.05),(x+w-.08,y,z+.05),(x+w-.08,y,z+h-.06),(x+.08,y,z+h-.06)]
    b=[(x,front,z),(x+w,front,z),(x+w,front,z+h),(x,front,z+h)]
    for i in range(4):
        j=(i+1)%4
        m.quad([a[i],b[i],b[j],a[j]],'mid' if i==2 else 'steel',double=True,outline=True)
    _front(m,x,front+.002,z,w,h,'mid',outline=True)
    # Recessed, nearly 4:3 glass with a visibly thicker control chin.
    glass=m.part('crt-glass')
    _front(glass,x+.045,front+.005,z+.075,w-.09,h-.11,'ink',outline=True)
    _front(glass,x+.066,front+.007,z+.094,w-.132,h-.148,'dark')
    # Thin glass highlight, not a luminous mint rectangle.
    details=m.part('crt-controls-and-content')
    _front(details,x+.077,front+.009,z+h-.087,w*.35,.012,'steel')
    for k in range(4):details.box(x+w*.59+k*.045,front+.007,z+.023,.025,.015,.012,'steel')
    details.box(x+w-.065,front+.009,z+.027,.014,.01,.014,'mint')
    # Tube cooling slots remain useful at a rotated view.
    for k in range(5):
        m.quad([(x+w-.067,y+.05+k*.044,z+.15),(x+w-.035,y+.08+k*.044,z+.15),
                (x+w-.035,y+.08+k*.044,z+.29),(x+w-.067,y+.05+k*.044,z+.29)],'dark',double=True)
    if cctv:
        # Four actual camera fields, each with ground line and tiny object.
        for row in range(2):
            for col in range(2):
                sx=x+.078+col*(w-.15)/2; sz=z+.103+row*(h-.16)/2
                sw=(w-.18)/2; sh=(h-.19)/2
                _front(details,sx,front+.011,sz,sw,sh,'steel')
                _front(details,sx+.015,front+.012,sz+.023,sw-.03,.012,'mid')
                _front(details,sx+sw*.59,front+.013,sz+.045,.025,sh*.45,'dark')
                _front(details,sx+.014,front+.013,sz+sh-.027,.038,.009,'paper')
        scan=m.part('cctv-scan-line','cctv-scan')
        _front(scan,x+.077,front+.015,z+.25,w-.154,.009,'paper',opacity=.5)
    else:
        terminal=m.part('system-lines','sys-type')
        for j,width in enumerate((.36,.26,.32,.17)):
            _front(terminal,x+.087,front+.011,z+h-.13-j*.043,min(width,w-.19),.025,'mint')
        cursor=m.part('system-cursor','sys-type')
        _front(cursor,x+.27,front+.014,z+.139,.032,.012,'mint')


def _desk(m,cctv=False):
    m.box(.025,0,.735,1.6,.73,.055,'steel',top='mid')
    m.box(.045,.02,.665,1.56,.045,.07,'dark')
    # Left pedestal has three operable drawer fronts; right side is open.
    m.box(.075,.075,.08,.38,.59,.65,'steel')
    m.box(.065,.06,.035,.4,.6,.045,'dark')
    for z,h in ((.105,.17),(.29,.17),(.475,.21)):_drawer(m,.091,.672,z,.348,h)
    for x in (1.50,):
        for y in (.045,.63):m.box(x,y,.035,.052,.052,.7,'steel')
    m.box(1.49,.02,.025,.08,.69,.025,'dark')
    m.box(.43,.025,.19,1.08,.035,.36,'dark')
    # Under-desk computer, with optical drive, air intake, and status light.
    m.box(1.17,.16,.075,.25,.48,.55,'paper')
    tower=m.part('tower-face')
    _front(tower,1.188,.643,.38,.212,.195,'mid',outline=True)
    _front(tower,1.204,.647,.502,.178,.035,'dark')
    _front(tower,1.221,.650,.514,.12,.008,'mid')
    for k in range(5):_front(tower,1.202,.647,.16+k*.026,.18,.01,'steel')
    tower.box(1.352,.648,.41,.018,.01,.018,'mint')
    # Swivel base and neck hold the heavy tube clear of the tabletop.
    m.cylinder(.865,.305,.793,.19,.035,'steel',sides=12)
    m.box(.79,.235,.828,.15,.14,.085,'mid')
    _crt(m,.545,.055,.906,cctv=cctv)
    # Keyboard has a raised rear edge, separate keys, and a space bar.
    m.box(.565,.545,.793,.58,.16,.025,'paper')
    keys=m.part('keyboard-keys')
    for row in range(3):
        for col in range(10):
            _top(keys,.586+col*.052,.558+row*.037,.820,.038,.025,'mid')
    _top(keys,.706,.674,.820,.215,.022,'mid')
    m.box(1.235,.54,.791,.095,.115,.025,'paper')
    _top(keys,1.279,.548,.819,.008,.042,'steel')
    # Closed ledger, paper slips, and clipped pen on the free left surface.
    m.box(.10,.35,.793,.31,.265,.025,'dark')
    m.box(.112,.357,.819,.292,.246,.012,'paper')
    _top(keys,.13,.371,.833,.014,.214,'mid')
    for j in range(4):_top(keys,.17,.39+j*.036,.834,.18,.006,'mid')
    m.box(.435,.38,.796,.012,.19,.012,'ink')
    # South chair is pulled away enough to read as a working place.
    m.cylinder(.825,1.10,.055,.07,.345,'steel')
    for a in range(5):
        ang=a*2*pi/5
        end=(.825+.27*cos(ang),1.10+.27*sin(ang),.055)
        _bar(m,(.825,1.10,.09),end,.019,'steel')
        m.box(end[0]-.026,end[1]-.026,.012,.052,.052,.037,'dark')
    m.box(.595,.88,.405,.46,.40,.065,'dark',top='steel')
    m.box(.62,1.245,.47,.035,.04,.34,'steel')
    m.box(.99,1.245,.47,.035,.04,.34,'steel')
    m.box(.60,1.22,.68,.44,.08,.24,'dark',top='steel')


def _toilet(m):
    # Tank back is exactly y=0, ready to sit against the room's north wall.
    m.box(.13,0,.46,.54,.245,.535,'paper')
    m.box(.115,0,.995,.57,.26,.045,'paper',top='white')
    m.box(.665,.14,.84,.045,.065,.055,'steel')
    _front(m,.675,.208,.858,.025,.016,'mid')
    # Wide floor foot narrows at the neck and expands into an oval bowl.
    _loft(m,[_oval(.40,.64,.22,.32,.025),_oval(.40,.64,.205,.30,.075),
             _oval(.40,.61,.155,.22,.26),_oval(.40,.665,.245,.335,.43)],'paper',cap=False)
    _loft(m,[_oval(.40,.665,.245,.335,.43),_oval(.40,.68,.27,.35,.49)],'paper',cap=False)
    # Dark recessed cavity under an open ring reads at the scene's scale.
    m.quad(_oval(.40,.69,.18,.255,.452),'dark')
    _oval_ring(m,.40,.68,.278,.36,.186,.263,.49,.055)
    # Seat hinge block and separate raised lid lean back toward the tank.
    m.box(.19,.29,.50,.42,.08,.08,'paper')
    lid=[(.16,.305,.57),(.64,.305,.57),(.64,.232,.96),(.58,.218,1.01),
         (.22,.218,1.01),(.16,.232,.96)]
    m.quad(lid,'white',double=True,outline=True)
    m.quad([(.205,.308,.62),(.595,.308,.62),(.595,.245,.93),
            (.55,.235,.962),(.25,.235,.962),(.205,.245,.93)],'paper',double=True)
    # Integrated side washlet controls project only to the stated footprint.
    m.box(.676,.46,.455,.108,.27,.07,'paper')
    _top(m,.691,.48,.527,.078,.214,'steel')
    for j in range(3):_top(m,.703,.50+j*.053,.529,.045,.026,'mid')
    _top(m,.703,.672,.529,.020,.012,'mint')
    # Rear supply valve/short pipe is part of the fixture, not a side holder.
    _bar(m,(.09,.12,.08),(.09,.12,.46),.013,'steel')
    _bar(m,(.09,.12,.46),(.13,.12,.46),.013,'steel')


def _basin(m):
    # Wall mounting, exposed trap, and an actual shallow open basin.
    m.box(.06,0,.78,.53,.045,.13,'steel')
    _loft(m,[_oval(.325,.26,.18,.14,.70),_oval(.325,.26,.285,.215,.87)],'paper',cap=False)
    _oval_ring(m,.325,.26,.295,.225,.235,.163,.87,.045)
    m.quad(_oval(.325,.26,.235,.163,.856),'mid')
    m.cylinder(.325,.27,.857,.029,.008,'dark',sides=8)
    _bar(m,(.325,.26,.705),(.325,.26,.48),.028,'steel')
    _bar(m,(.325,.26,.48),(.325,.095,.48),.028,'steel')
    _bar(m,(.325,.095,.48),(.325,.02,.56),.028,'steel')
    m.cylinder(.325,.075,.91,.026,.155,'steel',sides=8)
    _bar(m,(.325,.075,1.065),(.325,.24,1.065),.025,'steel')
    _bar(m,(.325,.24,1.065),(.325,.24,1.025),.021,'steel')
    m.box(.39,.06,.932,.10,.026,.02,'mid')


def _stockrack(m):
    for x in (.025,1.335):
        for y in (.025,.485):
            m.box(x,y,.015,.04,.04,1.735,'steel')
            for z in (.18,.60,1.02,1.44):_front(m,x+.012,y+.041,z,.014,.027,'ink')
    for z in (.13,.61,1.09,1.57):
        m.box(.015,.015,z,1.37,.52,.045,'steel',top='mid')
        m.box(.025,.49,z-.035,1.35,.035,.035,'dark')
    # Stock is deliberately varied: low crates, taped cartons, a top archive.
    _crate(m,.07,.075,.175,.53,.39,.30)
    _carton(m,.69,.075,.175,.58,.40,.39)
    _carton(m,.08,.065,.655,.43,.42,.33)
    _carton(m,.57,.075,.655,.34,.39,.28)
    _carton(m,.965,.085,.655,.31,.38,.36)
    _crate(m,.08,.07,1.135,.54,.39,.30)
    _carton(m,.71,.075,1.135,.57,.40,.32)
    _carton(m,.07,.085,1.615,.42,.37,.12)
    _carton(m,.61,.085,1.615,.53,.37,.12)
    # Rear diagonal brace stays behind the boxes.
    _bar(m,(.07,.03,.2),(1.32,.03,1.55),.012,'dark')


def _lockers(m):
    m.box(.025,.025,.06,.95,.42,1.79,'steel')
    m.box(.01,.01,1.85,.98,.48,.045,'mid')
    m.box(.055,.055,.025,.89,.37,.035,'dark')
    doors=m.part('locker-doors')
    details=m.part('locker-vents-and-hardware')
    for x in (.045,.515):
        _front(doors,x,.45,.105,.435,1.71,'mid',outline=True)
        # Louvres at both top and bottom; tiny light upper edge, dark slit.
        for z0 in (.20,1.53):
            for j in range(4):
                _front(details,x+.087,.453,z0+j*.036,.26,.013,'dark')
                _front(details,x+.087,.455,z0+j*.036+.013,.26,.006,'paper')
        # Stamped card window and recessed handle surround a small keyhole.
        _front(details,x+.135,.457,1.325,.17,.07,'steel',outline=True)
        _front(details,x+.152,.46,1.342,.136,.037,'paper')
        _front(details,x+.322,.459,.91,.072,.19,'steel',outline=True)
        details.box(x+.337,.46,.947,.02,.034,.11,'dark')
        _front(details,x+.348,.495,.918,.014,.016,'ink')
        for z in (.32,1.52):details.box(x-.005,.451,z,.023,.025,.10,'paper')


def _utility(m):
    m.box(.025,.035,.095,.85,.60,.765,'steel')
    for x in (.06,.795):
        for y in (.075,.55):m.box(x,y,.02,.045,.045,.075,'steel')
    # Cabinet pair and an open kick beneath.
    doors=m.part('utility-cabinet-doors')
    for x in (.045,.458):
        _front(doors,x,.642,.15,.395,.65,'mid',outline=True)
        doors.box(x+.28,.646,.64,.025,.035,.12,'dark')
    m.box(.01,.015,.86,.88,.67,.055,'mid',top='paper')
    m.box(.015,.015,.915,.87,.035,.15,'steel')
    # Raised steel lip and recessed sink are built from four strips.
    _top(m,.09,.125,.917,.43,.43,'steel',outline=True)
    _top(m,.13,.165,.919,.35,.35,'dark')
    _top(m,.145,.18,.922,.32,.32,'steel')
    m.cylinder(.305,.35,.923,.026,.006,'dark')
    m.cylinder(.30,.09,.918,.025,.20,'steel')
    _bar(m,(.30,.09,1.118),(.30,.29,1.118),.024,'steel')
    _bar(m,(.30,.29,1.118),(.30,.29,1.065),.021,'steel')
    m.box(.55,.24,.918,.25,.31,.028,'paper')
    for j in range(5):_top(m,.57,.26+j*.052,.949,.21,.007,'mid')
    # Cleaning bottle, restrained gray plastic with a narrow pump.
    m.box(.69,.07,.918,.085,.095,.155,'paper')
    m.box(.719,.09,1.073,.025,.025,.045,'steel')
    m.box(.718,.085,1.11,.065,.025,.02,'steel')


def _tea(m):
    m.box(.025,.025,.06,1.05,.495,.83,'steel')
    m.box(.01,.015,.89,1.08,.52,.055,'mid',top='paper')
    doors=m.part('tea-cabinet-doors')
    for x in (.05,.56):
        _front(doors,x,.523,.13,.485,.70,'mid',outline=True)
        doors.box(x+.31,.525,.68,.115,.022,.022,'dark')
    # Insulated electric pot: squat steel body, closed lid, spout and grip.
    m.cylinder(.32,.28,.947,.165,.035,'dark',sides=12)
    _loft(m,[_oval(.32,.28,.135,.13,.982),_oval(.32,.28,.155,.145,1.12),
             _oval(.32,.28,.125,.12,1.28)],'paper')
    m.cylinder(.32,.28,1.28,.13,.035,'steel',sides=12)
    m.box(.295,.26,1.315,.05,.045,.035,'dark')
    # Handle is an open angular loop, so the kettle reads as equipment.
    _bar(m,(.20,.26,1.235),(.11,.26,1.245),.026,'dark')
    _bar(m,(.11,.26,1.245),(.08,.26,1.075),.026,'dark')
    _bar(m,(.08,.26,1.075),(.20,.26,1.065),.026,'dark')
    _bar(m,(.43,.285,1.105),(.55,.285,1.21),.04,'mid')
    m.cylinder(.32,.285,.95,.023,.005,'mint')
    _front(m,.285,.428,1.085,.07,.09,'mid')
    _front(m,.302,.431,1.103,.036,.054,'steel')
    # Ceramic cup with open mouth, saucer and loop handle.
    m.cylinder(.79,.30,.947,.105,.016,'paper',sides=12)
    _loft(m,[_oval(.79,.30,.061,.061,.965),_oval(.79,.30,.075,.075,1.10)],'paper',cap=False)
    _oval_ring(m,.79,.30,.075,.075,.057,.057,1.10,.013,'white')
    m.quad(_oval(.79,.30,.055,.055,1.09),'dark')
    for a,b in [((.854,.30,1.075),(.91,.30,1.075)),((.91,.30,1.075),(.91,.30,1.005)),((.91,.30,1.005),(.852,.30,1.005))]:_bar(m,a,b,.013,'paper')
    m.box(.935,.09,.947,.10,.13,.17,'paper')
    _front(m,.955,.223,1.00,.061,.06,'mid')
    steam=m.part('kettle-steam','kettle-steam')
    for j,(x,z) in enumerate(((.54,1.28),(.57,1.37),(.55,1.45))):
        steam.quad([(x-.012,.285,z),(x+.015,.285,z+.04),(x+.029,.285,z+.025),(x,.285,z-.01)],'paper',opacity=.32,double=True)


def _cart(m):
    # Four dark casters, two open load decks and a tall push handle.
    for x in (.075,.685):
        for y in (.075,.445):
            m.box(x-.023,y-.015,.07,.046,.03,.055,'steel')
            m.box(x-.035,y-.038,.015,.07,.076,.065,'dark',top='steel')
    m.box(.015,.015,.135,.77,.52,.045,'steel',top='mid')
    m.box(.015,.015,.53,.77,.52,.035,'steel',top='mid')
    for x in (.035,.73):
        for y in (.035,.48):m.box(x,y,.18,.032,.032,.35,'steel')
    _bar(m,(.05,.055,.555),(.05,.055,.85),.022,'mid')
    _bar(m,(.74,.055,.555),(.74,.055,.85),.022,'mid')
    _bar(m,(.05,.055,.85),(.74,.055,.85),.025,'dark')
    _carton(m,.075,.12,.18,.31,.34,.28)
    _carton(m,.43,.12,.18,.28,.34,.24)
    _carton(m,.08,.12,.565,.35,.35,.26)
    _carton(m,.47,.15,.565,.25,.31,.19)


def _stool(m):
    for x in (.065,.34):
        for y in (.065,.34):
            _bar(m,(x,y,.025),(x*.87+.025,y*.87+.025,.53),.023,'steel')
    _bar(m,(.07,.07,.22),(.35,.07,.22),.015,'steel')
    _bar(m,(.07,.35,.22),(.35,.35,.22),.015,'steel')
    _bar(m,(.07,.07,.22),(.07,.35,.22),.015,'steel')
    _bar(m,(.35,.07,.22),(.35,.35,.22),.015,'steel')
    m.cylinder(.225,.225,.53,.215,.055,'dark',sides=12)
    m.cylinder(.225,.225,.585,.205,.015,'steel',sides=12)


def _baskets(m):
    # Nested baskets retain their open center and vented front/side walls.
    for k in range(3):
        z=.025+k*.105
        w=.49+k*.015;d=.36+k*.02;x=(.55-w)/2;y=(.45-d)/2
        m.box(x+.025,y+.025,z,w-.05,d-.05,.023,'dark')
        for xx in (x,x+w-.025):
            for yy in (y,y+d-.025):m.box(xx,yy,z,.025,.025,.19,'steel')
        for j in range(5):
            xx=x+.05+j*(w-.1)/4
            m.box(xx,y,z,.017,.018,.18,'steel')
            m.box(xx,y+d-.018,z,.017,.018,.18,'steel')
        for j in range(3):
            yy=y+.05+j*(d-.1)/2
            m.box(x,yy,z,.018,.017,.18,'steel')
            m.box(x+w-.018,yy,z,.018,.017,.18,'steel')
        m.box(x,y,z+.17,w,.025,.028,'mid')
        m.box(x,y+d-.025,z+.17,w,.025,.028,'mid')
        m.box(x,y,z+.17,.025,d,.028,'mid')
        m.box(x+w-.025,y,z+.17,.025,d,.028,'mid')
    _bar(m,(.09,.06,.42),(.46,.06,.42),.012,'dark')


def _umbrella(m):
    # A perforated stand with folded umbrellas, not a tiny parasol tree.
    m.box(.035,.035,.025,.48,.38,.035,'steel')
    for x in (.055,.465):
        for y in (.055,.345):m.box(x,y,.055,.025,.025,.42,'steel')
    for z in (.14,.30,.45):
        m.box(.055,.055,z,.435,.022,.025,'mid')
        m.box(.055,.345,z,.435,.022,.025,'mid')
        m.box(.055,.055,z,.022,.315,.025,'mid')
        m.box(.465,.055,z,.022,.315,.025,'mid')
    for x,y,z in ((.15,.15,.98),(.29,.25,1.045),(.405,.16,.91)):
        _bar(m,(x,y,.07),(x-.025,y,z-.13),.012,'steel')
        _loft(m,[_oval(x,y,.024,.018,.12),_oval(x-.01,y,.054,.035,.35),
                 _oval(x-.022,y,.035,.025,z-.18)],'dark')
        _bar(m,(x-.025,y,z-.13),(x-.025,y,z-.035),.017,'mid')
        _bar(m,(x-.025,y,z-.035),(x+.025,y,z-.015),.017,'mid')
        _bar(m,(x+.025,y,z-.015),(x+.052,y,z-.055),.017,'mid')


def _human(m,coat='steel'):
    """A compact adult RPG silhouette, with connected clothing and swept hair.

    The small face and a few large clothing planes stay readable at scene size.
    coat='mint' selects the clerk's broad apron; the shirt stays muted.
    """
    # Solid trouser legs overlap the coat hem; shoes have one clear toe plane.
    for x,y in ((.075,.095),(.245,.105)):
        m.box(x,y,.025,.14,.245,.085,'dark',top='steel')
        m.box(x+.008,y+.012,.105,.124,.176,.575,'dark',top='steel')
    body=m.part('operator-breath','breathe')
    # A single six-sided tunic, wide across the shoulders and gently tapered.
    front=[(.072,.305,.625),(.378,.305,.625),(.386,.295,1.185),
           (.347,.285,1.305),(.103,.285,1.305),(.064,.295,1.185)]
    back=[(x,.10,z) for x,y,z in front]
    body.quad(front,'steel',double=True,outline=True)
    body.quad(list(reversed(back)),'dark',double=True,outline=False)
    for i in range(len(front)):
        j=(i+1)%len(front)
        body.quad([back[i],back[j],front[j],front[i]],
                  'mid' if i==3 else 'dark',double=True,outline=False)
    # Sleeves are broad, connected masses, with no outlined elbow joints.
    for x in (.018,.347):
        body.box(x,.13,.82,.086,.195,.405,'steel',top='mid')
    # A small dark neckline avoids long bright anatomy lines down the coat.
    _front(body,.173,.299,1.222,.104,.065,'dark')
    body.quad([(.174,.301,1.288),(.225,.304,1.235),(.276,.301,1.288)],
              'paper',double=True)
    # Neck is mostly behind the coat and head, rather than a separate joint.
    body.box(.177,.15,1.275,.096,.105,.105,'paper')
    # The angular head is one broad block with a quiet three-quarter face.
    body.box(.104,.095,1.345,.242,.228,.245,'paper',top='mid')
    # An asymmetrical swept crown has only a few large planes, no wireframe.
    lower=[(.086,.085,1.555),(.349,.085,1.555),(.363,.285,1.555),
           (.326,.334,1.555),(.145,.334,1.555),(.086,.29,1.555)]
    upper=[(.111,.093,1.635),(.317,.093,1.65),(.346,.274,1.625),
           (.309,.317,1.62),(.146,.317,1.62),(.103,.275,1.62)]
    for i in range(len(lower)):
        j=(i+1)%len(lower)
        body.quad([lower[i],lower[j],upper[j],upper[i]],
                  'dark' if i<3 else 'ink',double=True,outline=False)
    body.quad(upper,'steel',double=True,outline=True)
    # Large side-swept fringe makes a hairstyle instead of a faceted helmet.
    body.quad([(.096,.331,1.588),(.312,.331,1.588),(.237,.336,1.523),
               (.166,.336,1.49),(.108,.334,1.516)],'dark',double=True)
    _front(body,.098,.327,1.439,.031,.11,'dark')
    _front(body,.319,.327,1.47,.026,.09,'dark')
    # Two one-pixel eyes and a small cheek plane; no outlined nose or mouth.
    _front(body,.215,.326,1.465,.018,.017,'dark')
    _front(body,.291,.326,1.468,.014,.017,'dark')
    _front(body,.273,.327,1.414,.035,.035,'mid')
    # Apron/bib is a broad uninterrupted color mass, especially for the clerk.
    apron=m.part('operator-apron','apron-sway')
    apron.quad([(.091,.311,.62),(.359,.311,.62),(.332,.312,.96),
                (.312,.309,1.192),(.138,.309,1.192),(.118,.312,.96)],
               coat,double=True,outline=False)
    pocket='dark' if coat != 'mint' else 'steel'
    _front(apron,.157,.315,.805,.137,.105,pocket)
    _front(apron,.16,.317,.895,.131,.014,'mid')
    # Hands are simple pale mitten blocks, visually joined to the cuffs.
    body.box(.351,.197,.729,.071,.12,.105,'paper',top='paper')
    hand=m.part('operator-hand','hand')
    hand.box(.023,.197,.729,.071,.12,.105,'paper',top='paper')


def build(model,kind,coat='steel'):
    """Populate an existing mesh.Model; dimensions are in FOOTPRINTS.

    A clerk may pass coat='mint'; the default night operator is muted steel.
    Only the small named pieces have motion hooks, not whole furniture.
    """
    if kind in ('sys_desk','cctv_desk'):_desk(model,kind=='cctv_desk')
    elif kind == 'human':_human(model,coat)
    else:
        builders={'toilet':_toilet,'wall_basin':_basin,'stockrack':_stockrack,
                  'lockers':_lockers,'utility':_utility,'tea_counter':_tea,
                  'cart':_cart,'stool':_stool,'baskets':_baskets,'umbrella':_umbrella}
        if kind not in builders:raise ValueError('Unknown back-room model: '+kind)
        builders[kind](model)
    return model
