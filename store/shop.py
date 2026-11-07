"""Original metre-scale shop fixtures, built entirely from palette geometry.

Fresh construction references (photos inspected before drawing):
Fuji FCMD300ML, Panasonic NE-1802, Toshiba WILLPOS A20,
TAIJI OS-600N, and SDRS RSD-F/GSR-C cases.  These are observations of
functional construction, not copied meshes, images, logos, or pack designs.
"""
from math import cos, sin, pi


FOOTPRINTS = {
    'checkout': (2.0, .85, 1.5),
    'warmer': (1.0, .6, 1.5),
    'microwave': (.85, .65, 1.5),
    'coffee': (1.0, .8, 2.0),
    'magazines': (.6, 1.7, 1.4),
    'gondola_snacks': (1.05, 3.0, 1.45),
    'gondola_noodles': (1.05, 3.0, 1.45),
    'gondola_bread': (1.05, 3.0, 1.45),
    'fresh_case': (.75, 2.7, 1.9),
    'bento_case': (.75, 2.7, 1.9),
    'dairy_case': (.75, 2.7, 1.9),
    'freezer': (1.6, .9, .9),
    'drink_wall': (3.4, .75, 1.9),
}


def _prism(m, lower, upper, color, top=None):
    """Two equal-length polygon rings; preserve visible facets and hard edges."""
    m.quad(upper, top or color, outline=True)
    for i in range(len(lower)):
        j = (i + 1) % len(lower)
        m.quad([lower[i], lower[j], upper[j], upper[i]],
               color if i % 3 else 'steel', outline=True)


def _rect_ring(x, y, z, w, d, inset=0):
    return [(x+inset, y+inset, z), (x+w-inset, y+inset, z),
            (x+w-inset, y+d-inset, z), (x+inset, y+d-inset, z)]


def _front(m, x, y, z, w, h, color, alpha=1):
    m.quad([(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)],
           color, alpha, double=True)


def _west(m, x, y, z, d, h, color, alpha=1):
    m.quad([(x,y,z),(x,y,z+h),(x,y+d,z+h),(x,y+d,z)],
           color, alpha, double=True)


def _top(m, x, y, z, w, d, color, alpha=1):
    m.quad([(x,y,z),(x+w,y,z),(x+w,y+d,z),(x,y+d,z)],
           color, alpha, double=True)


def _feet(m, w, d, inset=.07, h=.09):
    for x in (inset, w-inset-.065):
        for y in (inset, d-inset-.065):
            m.box(x,y,0,.065,.065,h,'dark')


def _cabinet(m, w, d, h=.9):
    _feet(m,w,d)
    m.box(.035,.035,.075,w-.07,d-.07,h-.12,'dark',top='steel')
    m.box(.02,.015,h-.06,w-.04,d-.03,.06,'paper',top='paper')
    # Separate doors, a recessed plinth, and small vertical pulls.
    split=w*.51
    m.box(.065,d-.032,.16,split-.085,.025,h-.30,'steel',top='steel')
    m.box(split+.01,d-.032,.16,w-split-.075,.025,h-.30,'steel',top='steel')
    for x in (split-.07,split+.035):
        m.box(x,d-.018,h-.34,.018,.012,.12,'mid')
    m.box(.08,d-.020,.12,w-.16,.018,.025,'ink')


def _tag(m, x, y, z, side='west', mint=False):
    if side=='west':
        _west(m,x,y,z,.13,.038,'paper')
        _west(m,x-.001,y+.018,z+.012,.056,.012,'dark')
        if mint: _west(m,x-.002,y+.096,z+.006,.025,.025,'mid')
    else:
        _front(m,x,y,z,.13,.038,'paper')
        _front(m,x+.018,y+.001,z+.012,.056,.012,'dark')
        if mint: _front(m,x+.096,y+.002,z+.006,.025,.025,'mid')


def _bag(m, x,y,z,w=.25,d=.16,h=.30,color='paper',variant=0):
    # A pinched pillow pack: broad belly, tapered seam, visible folded sides.
    a=_rect_ring(x,y,z,w,d,.025)
    b=_rect_ring(x,y,z+h*.77,w,d,0)
    _prism(m,a,b,color,top=color)
    c=[(x+.025,y+d*.38,z+h),(x+w-.025,y+d*.38,z+h),
       (x+w-.025,y+d*.62,z+h),(x+.025,y+d*.62,z+h)]
    _prism(m,b,c,color,top='mid')
    m.box(x+.017,y+d*.36,z+h-.017,w-.034,d*.28,.018,'mid')
    face='dark' if color!='dark' else 'paper'
    _front(m,x+w*.18,y+d+.002,z+h*.30,w*.64,h*.21,face)
    _west(m,x-.002,y+d*.17,z+h*.26,d*.66,h*.26,face)
    _front(m,x+w*.25,y+d+.003,z+h*.62,w*.43,.018,'mid')


def _cup(m, x,y,z,r=.11,h=.23,color='paper',lid='white'):
    n=8
    a=[(x+r*.77*cos(2*pi*i/n),y+r*.77*sin(2*pi*i/n),z) for i in range(n)]
    b=[(x+r*cos(2*pi*i/n),y+r*sin(2*pi*i/n),z+h) for i in range(n)]
    _prism(m,a,b,color,top=lid)
    m.cylinder(x,y,z+h,r*1.04,.026,lid,8)
    _front(m,x-r*.62,y+r*.91,z+h*.32,r*1.24,h*.24,'steel')
    _west(m,x-r*.91,y-r*.5,z+h*.3,r,.055,'mid')


def _bottle(m, x,y,z,r=.065,h=.30,color='paper',cap='mid'):
    m.cylinder(x,y,z,r,h*.69,color,8)
    a=[(x+r*cos(2*pi*i/8),y+r*sin(2*pi*i/8),z+h*.69) for i in range(8)]
    b=[(x+r*.43*cos(2*pi*i/8),y+r*.43*sin(2*pi*i/8),z+h*.85) for i in range(8)]
    _prism(m,a,b,color,top=color)
    m.cylinder(x,y,z+h*.85,r*.43,h*.10,color,8)
    m.cylinder(x,y,z+h*.95,r*.49,h*.05,cap,8)
    _front(m,x-r*.75,y+r*.87,z+h*.27,r*1.5,h*.25,'white' if color!='paper' else 'mid')
    _west(m,x-r*.88,y-r*.55,z+h*.27,r*1.1,h*.25,'mid')


def _carton(m,x,y,z,w=.14,d=.14,h=.28,color='paper'):
    m.box(x,y,z,w,d,h*.77,color,top=color)
    _prism(m,_rect_ring(x,y,z+h*.77,w,d),
           [(x,y+d*.42,z+h),(x+w,y+d*.42,z+h),
            (x+w,y+d*.58,z+h),(x,y+d*.58,z+h)],color,top='white')
    m.box(x+.01,y+d*.41,z+h-.008,w-.02,d*.18,.012,'mid')
    _front(m,x+w*.17,y+d+.002,z+h*.22,w*.66,h*.31,'steel')
    _west(m,x-.002,y+d*.20,z+h*.24,d*.6,h*.28,'white')


def _loaf(m,x,y,z,w=.28,d=.19,h=.15,wrapped=True):
    # Cut-corner loaf silhouette; paper/grey remains in the restrained palette.
    k=.035
    outline=[(x+k,y,z),(x+w-k,y,z),(x+w,y+k,z),(x+w,y+d-k,z),
             (x+w-k,y+d,z),(x+k,y+d,z),(x,y+d-k,z),(x,y+k,z)]
    upper=[(a,b,z+h) for a,b,_ in outline]
    _prism(m,outline,upper,'paper',top='paper')
    for i in range(3):
        xx=x+.055+i*(w-.09)/3
        m.quad([(xx,y+.035,z+h+.002),(xx+.025,y+.035,z+h+.002),
                (xx+.065,y+d-.03,z+h+.002),(xx+.04,y+d-.03,z+h+.002)],'mid')
    if wrapped:
        _front(m,x+.025,y+d+.002,z+.015,w-.05,h*.55,'mid',.55)
        m.box(x+w*.70,y+.01,z+h+.003,.04,d-.02,.012,'steel')


def _tray(m,x,y,z,w=.28,d=.20,h=.045,variant=0):
    m.box(x,y,z,w,d,h,'dark',top='mid')
    # Compartments contain rice, vegetables, or two larger meal portions.
    m.box(x+.018,y+.015,z+h,w*.43,d-.03,.023,'paper',top='white')
    m.box(x+w*.52,y+.018,z+h,w*.40,d*.40,.027,'steel',top='mid')
    m.box(x+w*.52,y+d*.56,z+h,w*.25,d*.33,.025,'paper')
    if variant%2: m.box(x+w*.81,y+d*.58,z+h,w*.10,d*.25,.022,'mid')
    _top(m,x-.003,y-.003,z+h+.032,w+.006,d+.006,'white',.12)
    m.box(x+w*.37,y-.005,z+h+.034,w*.18,d+.01,.006,'paper')


def _checkout(m):
    _cabinet(m,2,.85,1.0)
    m.box(.04,.79,.87,1.92,.045,.06,'mid')
    m.box(.09,.82,.24,1.82,.025,.55,'dark')
    m.box(.12,.840,.75,.25,.005,.045,'paper')
    m.box(.12,.844,.75,.035,.006,.045,'mint')
    # Cash drawer carries the main POS, well clear of the printer.
    m.box(.73,.12,1.0,.48,.38,.075,'dark',top='steel')
    _front(m,.77,.501,1.018,.39,.022,'ink')
    m.box(.90,.24,1.07,.13,.15,.15,'steel')
    # Slightly inclined display shell with visible thickness and top edge.
    low=[(.74,.23,1.21),(1.19,.23,1.21),(1.19,.30,1.21),(.74,.30,1.21)]
    high=[(.74,.13,1.50),(1.19,.13,1.50),(1.19,.20,1.50),(.74,.20,1.50)]
    _prism(m,low,high,'dark',top='steel')
    m.quad([(.77,.302,1.245),(1.16,.302,1.245),(1.16,.214,1.465),(.77,.214,1.465)],'ink',double=True)
    m.quad([(.79,.292,1.275),(1.04,.292,1.275),(1.04,.235,1.425),(.79,.235,1.425)],'steel',double=True)
    # A separate customer display, scanner cradle, card terminal, and coin tray.
    m.box(1.37,.42,1,.075,.075,.18,'steel')
    m.box(1.24,.42,1.18,.34,.075,.17,'dark',top='steel')
    _front(m,1.27,.497,1.21,.28,.10,'ink')
    m.box(.25,.33,1,.14,.18,.045,'dark')
    m.box(.285,.34,1.04,.075,.11,.14,'steel')
    m.box(.272,.415,1.15,.10,.10,.085,'dark')
    _front(m,.285,.517,1.17,.073,.035,'ink')
    m.box(1.65,.49,1,.23,.26,.045,'dark',top='steel')
    m.box(1.68,.53,1.045,.17,.16,.11,'steel',top='ink')
    m.box(1.09,.64,1,.35,.14,.025,'mid',top='dark')
    # Standalone thermal printer with an emerging receipt and cutter lip.
    m.box(.45,.14,1,.23,.28,.17,'paper',top='mid')
    m.box(.47,.18,1.17,.19,.20,.045,'mid')
    m.box(.478,.384,1.105,.175,.016,.028,'ink')
    m.box(.47,.403,1.088,.19,.022,.018,'steel')
    motion=m.part('printer-receipt','paper-feed')
    motion.quad([(.49,.407,1.12),(.64,.407,1.12),(.64,.46,1.20),(.49,.46,1.20)],'white',double=True)
    for z in (1.14,1.165):
        motion.quad([(.515,.424,z),(.605,.424,z),(.605,.432,z+.009),(.515,.432,z+.009)],'steel',double=True)
    screen=m.part('customer-display','display-scroll')
    _front(screen,1.29,.499,1.26,.12,.027,'mint')
    _front(screen,1.29,.499,1.225,.21,.012,'mid')


def _warmer(m):
    _cabinet(m,1,.6,.89)
    # Delicate glass showcase: separate base, canopy, sliding doors and rack.
    m.box(.05,.055,.89,.90,.49,.075,'steel',top='mid')
    for x in (.06,.91):
        for y in (.075,.50): m.box(x,y,.96,.028,.028,.46,'mid')
    m.box(.045,.05,1.425,.91,.50,.075,'mid',top='paper')
    m.box(.055,.515,1.43,.89,.023,.045,'paper')
    # Two wire trays, with the upper rack raised clear of foods below.
    for z in (.985,1.205):
        m.box(.085,.09,z,.825,.42,.022,'steel',top='mid')
        for y in (.12,.22,.32,.42): m.box(.09,y,z+.023,.81,.012,.008,'paper')
        m.box(.09,.49,z+.01,.81,.018,.028,'mid')
    for z in (1.015,1.235):
        for x,y,w in ((.12,.14,.20),(.38,.14,.18),(.62,.14,.22),(.17,.34,.22),(.53,.34,.25)):
            _loaf(m,x,y,z,w,.11,.075,False)
    # The glass tint is extremely light so the internal tray depth reads.
    _front(m,.09,.536,.97,.82,.44,'paper',.07)
    _west(m,.071,.10,.97,.40,.44,'paper',.09)
    m.box(.485,.535,1.06,.018,.018,.13,'mid')
    m.box(.52,.529,1.08,.018,.018,.13,'mid')
    m.box(.75,.539,.914,.10,.006,.025,'dark')
    light=m.part('warmer-canopy-lamp','warmer-light')
    _front(light,.12,.579,1.445,.70,.045,'mint')


def _microwave(m):
    _cabinet(m,.85,.65,.96)
    for x in (.10,.69):
        for y in (.11,.51): m.box(x,y,.96,.05,.045,.035,'dark')
    m.box(.07,.065,.995,.71,.51,.465,'mid',top='paper')
    m.box(.084,.572,1.02,.682,.018,.34,'paper',top='paper')
    # Deep door gasket, perforated viewing window and external door handle.
    m.box(.13,.59,1.075,.52,.018,.235,'dark',top='steel')
    _front(m,.15,.609,1.09,.47,.202,'ink')
    _front(m,.17,.611,1.108,.425,.166,'steel',.72)
    for row in range(3):
        _front(m,.18,.612,1.12+row*.047,.40,.010,'mid',.35)
    m.box(.659,.599,1.105,.025,.035,.18,'mid')
    m.box(.645,.61,1.10,.025,.035,.19,'paper')
    # Manufacturer-style horizontal membrane controls above the door.
    m.box(.087,.577,1.365,.676,.02,.073,'dark')
    _front(m,.105,.599,1.384,.117,.035,'ink')
    for i in range(8):
        m.box(.24+i*.056,.598,1.378,.045,.009,.041,'paper',top='paper')
    m.box(.697,.598,1.378,.045,.009,.041,'mint',top='mint')
    for x in (.13,.30,.47,.64):
        for row in range(2):
            _front(m,x,.594,1.027+row*.015,.105,.006,'dark')
    m.box(.07,.065,1.46,.71,.51,.025,'paper',top='paper')
    light=m.part('microwave-clock','display-scroll')
    _front(light,.127,.601,1.389,.063,.025,'mint')


def _coffee(m):
    _cabinet(m,1,.8,.88)
    # Stand machine to the left; right hand pocket holds lids and sugars.
    m.box(.075,.10,.88,.66,.58,.09,'dark',top='steel')
    m.box(.08,.11,.97,.65,.11,.78,'dark',top='steel')
    for x in (.08,.66): m.box(x,.22,.97,.07,.43,.47,'steel',top='dark')
    m.box(.085,.21,1.43,.64,.43,.34,'dark',top='steel')
    m.box(.11,.652,1.47,.59,.02,.265,'steel',top='mid')
    _front(m,.15,.675,1.515,.50,.175,'ink')
    # UI is modest monochrome, with one active mint indicator.
    for x in (.18,.34,.50):
        for z in (1.54,1.61):
            _front(m,x,.677,z,.10,.035,'mid')
    # Recessed cup bay with dispensing spout, drip grate and one paper cup.
    m.box(.20,.22,1.01,.39,.035,.40,'ink')
    m.box(.22,.44,.975,.37,.19,.025,'mid',top='dark')
    for i in range(5): m.box(.235+i*.063,.455,1.001,.018,.145,.008,'mid')
    m.cylinder(.41,.48,1.365,.052,.065,'mid',8)
    m.cylinder(.41,.49,1.335,.025,.035,'paper',8)
    _cup(m,.41,.51,1.012,.085,.20,'paper','dark')
    # Three distinct bean hoppers; dark contents are a geometric cluster.
    for x in (.105,.315,.525):
        m.box(x,.14,1.77,.185,.32,.20,'steel',top='mid')
        _front(m,x+.018,.462,1.79,.148,.12,'ink',.9)
        for dx,dy,dz in ((.05,.19,1.82),(.12,.20,1.84),(.075,.29,1.85)):
            m.cylinder(x+dx,dy,dz,.035,.035,'dark',6)
        m.box(x-.008,.13,1.97,.201,.34,.03,'paper',top='paper')
    m.box(.78,.16,.89,.16,.36,.17,'steel',top='dark')
    for z in (.98,1.005,1.03,1.055): m.cylinder(.86,.25,z,.068,.018,'paper',8)
    for i in range(3): m.box(.792+i*.041,.37,.99,.024,.12,.10,'paper',top='white')
    light=m.part('coffee-selection','display-scroll')
    _front(light,.50,.68,1.54,.10,.035,'mint')
    steam=m.part('coffee-steam','steam')
    for x,z in ((.385,1.25),(.425,1.29)):
        steam.quad([(x,.51,z),(x+.012,.51,z),(x+.022,.51,z+.045),(x+.01,.51,z+.045)],'paper',.55,double=True)


def _magazines(m):
    # Facing WEST: three stepped bins tilt back into the rack, not a wall of tiles.
    _feet(m,.6,1.7)
    m.box(.39,.07,.08,.14,1.56,1.25,'dark',top='steel')
    m.box(.06,.06,.09,.49,1.58,.08,'steel',top='mid')
    for y in (.06,1.60): m.box(.31,y,.16,.08,.04,1.22,'mid')
    for level,(xx,z) in enumerate(((.04,.20),(.16,.57),(.28,.94))):
        m.box(xx,.075,z,.24,1.55,.035,'steel',top='mid')
        m.box(xx,.075,z+.035,.025,1.55,.10,'mid',top='paper')
        for j in range(5):
            yy=.12+j*.295
            # The cover is a solid inclined board with its own thickness.
            low=[(xx+.05,yy,z+.05),(xx+.05,yy+.25,z+.05),
                 (xx+.075,yy+.25,z+.05),(xx+.075,yy,z+.05)]
            high=[(xx+.135,yy,z+.39),(xx+.135,yy+.25,z+.39),
                  (xx+.16,yy+.25,z+.39),(xx+.16,yy,z+.39)]
            col=['paper','mid','steel','paper','dark'][(j+level)%5]
            _prism(m,low,high,col,top='paper')
            # Cover masthead and editorial blocks are irregular, original marks.
            cover=lambda a,h,c: m.quad([(xx+.051+a*.25,yy+.025,z+.07+a),
                (xx+.051+a*.25,yy+.225,z+.07+a),
                (xx+.051+(a+h)*.25,yy+.225,z+.07+a+h),
                (xx+.051+(a+h)*.25,yy+.025,z+.07+a+h)],c,double=True)
            cover(.23,.035,'white')
            cover(.07,.09,'steel' if col=='paper' else 'paper')
        for yy in (.17,.76,1.35): _tag(m,xx-.002,yy,z+.048)
    m.box(.34,.075,1.34,.20,1.55,.06,'steel',top='mid')


def _gondola(m,kind):
    w=1.05; d=3
    # Three bolted standards and long T feet keep both sides physically legible.
    for y in (.10,1.47,2.84):
        m.box(.035,y,0,.98,.06,.075,'dark',top='steel')
        m.box(.486,y,.07,.078,.06,1.38,'mid',top='paper')
    m.box(.49,.08,.12,.07,2.83,1.28,'steel',top='mid')
    for y in (.115,1.49,2.855):
        for z in (.34,.76,1.18):
            _front(m,.508,y,z,.026,.045,'dark')
    for level,z in enumerate((.16,.59,1.02)):
        for side in (0,1):
            xx=.035 if side==0 else .56
            m.box(xx,.08,z,.455,2.84,.055,'steel',top='mid')
            edge=.035 if side==0 else .988
            m.box(edge,.08,z+.035,.027,2.84,.052,'paper',top='paper')
            for yy in (.15,.83,1.52,2.22):
                _tag(m,edge-.002 if side==0 else edge+.029,yy,z+.045,mint=(yy==2.22 and level==1))
            # Product rhythm changes within the bay; there is a shallow second row.
            x=.105 if side==0 else .62
            if kind=='gondola_snacks':
                for j in range(8):
                    yy=.14+j*.34
                    col=('paper','steel','mid','dark')[(j+level*2+side)%4]
                    _bag(m,x,yy,z+.057,.27,.22,.25+(j%3)*.027,col,(j+level+side)%7)
                    if j in (1,4,6):
                        _bag(m,x+.015,yy+.22,z+.057,.235,.08,.22,'mid',1)
            elif kind=='gondola_noodles':
                for j in range(9):
                    yy=.245+j*.295
                    if level==0 and j>5:
                        _bag(m,x-.01,yy-.10,z+.057,.28,.20,.18,'paper',1)
                    else:
                        _cup(m,x+.14,yy,z+.057,.12,.22+(j%2)*.025,
                             'paper' if j%3 else 'steel','white' if j%2 else 'mid')
            elif kind=='gondola_bread':
                for j in range(7):
                    yy=.14+j*.39
                    _loaf(m,x-.01,yy,z+.057,.29,.28,.14+(j%2)*.025)
                    if level==0 or j%3==1:
                        _loaf(m,x+.045,yy+.025,z+.21,.20,.22,.09)
    # End rails stop bags slipping into the aisle without forming solid walls.
    for y in (.075,2.905):
        m.box(.045,y,.17,.95,.022,.035,'mid')
        m.box(.045,y,1.025,.95,.022,.035,'mid')
    m.box(.47,.07,1.40,.11,2.85,.05,'paper',top='mid')


def _case(m, kind):
    # West-facing open case.  Rear duct, open shelves and shallow cheeks remain distinct.
    _feet(m,.75,2.7,.075,.075)
    m.box(.025,.025,.06,.70,2.65,.26,'paper',top='mid')
    m.box(.63,.025,.30,.095,2.65,1.51,'steel',top='mid')
    for y in (.025,2.62):
        # Clear end cheeks retain visible depth at the room's grazing view.
        # The independent front/rear jambs and upper rail carry the glass.
        for x in (.08,.605): m.box(x,y,.30,.025,.055,1.49,'mid',top='paper')
        m.box(.08,y,1.75,.55,.055,.04,'mid',top='paper')
        _front(m,.105,y+.027,.37,.50,1.36,'paper',.10)
    # Rear service housing and a slim suspended front light bridge leave the
    # open display visible from above instead of forming an opaque roof slab.
    m.box(.50,.025,1.80,.225,2.65,.10,'paper',top='paper')
    m.box(.025,.025,1.76,.065,2.65,.055,'mid',top='paper')
    # Separate rectangular ventilation slots run along the compressor plinth.
    for j in range(15):
        _west(m,.023,.13+j*.164,.12,.112,.052,'dark')
        _west(m,.022,.13+j*.164,.20,.112,.025,'steel')
    m.box(.02,.20,.28,.025,.29,.033,'steel')
    m.box(.018,.23,.289,.028,.14,.017,'ink')
    levels=(.34,.72,1.10,1.48)
    for level,z in enumerate(levels):
        m.box(.075,.085,z,.55,2.53,.045,'steel',top='mid')
        m.box(.055,.085,z+.024,.035,2.53,.045,'paper',top='white')
        for yy in (.16,.78,1.40,2.02): _tag(m,.052,yy,z+.032,mint=(yy==1.40 and level==0))
        # Vertical slots at the rear read as a perforated air duct, not product labels.
        for yy in (.21,.69,1.17,1.65,2.13):
            _west(m,.628,yy,z+.08,.18,.018,'dark')
        for j in range(7):
            yy=.12+j*.35
            if kind=='bento_case':
                _tray(m,.11,yy,z+.048,.39,.28,.042,j+level)
                if level<2 and j%3==0: _tray(m,.14,yy+.01,z+.132,.34,.25,.035,j)
            elif kind=='dairy_case':
                if level<2:
                    _carton(m,.12,yy,z+.048,.18,.15,.28,'paper' if j%3 else 'mid')
                    _carton(m,.34,yy,z+.048,.16,.15,.25,'paper')
                elif level==2:
                    _bottle(m,.23,yy+.095,z+.048,.074,.255,'paper','steel')
                    _bottle(m,.46,yy+.095,z+.048,.067,.24,'mid','paper')
                else:
                    _cup(m,.22,yy+.10,z+.048,.10,.15,'paper','white')
                    _cup(m,.46,yy+.10,z+.048,.085,.13,'mid','paper')
            else:
                if level in (0,2):
                    # Sandwich wedges stand upright in transparent folded packs.
                    x=.13; dd=.24; hh=.27
                    m.quad([(x,yy,z+.05),(x+.35,yy,z+.05),(x+.35,yy,z+.05+hh)],'paper',outline=True,double=True)
                    m.quad([(x,yy+dd,z+.05),(x+.35,yy+dd,z+.05+hh),(x+.35,yy+dd,z+.05)],'white',outline=True,double=True)
                    m.quad([(x,yy,z+.05),(x+.35,yy,z+.05+hh),(x+.35,yy+dd,z+.05+hh),(x,yy+dd,z+.05)],'paper',outline=True)
                    m.box(x+.21,yy+.01,z+.055,.038,dd-.02,.18,'steel')
                    if j%3==0: m.box(x+.255,yy+.02,z+.10,.019,dd-.04,.11,'mid')
                else:
                    _tray(m,.11,yy,z+.048,.39,.27,.048,j)
    # A small physical category plaque faces the public rear cross-aisle.
    # Bold silhouettes remain readable on the end panel without display text.
    _front(m,.215,2.679,.087,.305,.222,'steel')
    if kind=='dairy_case':
        _front(m,.294,2.683,.117,.150,.127,'paper')
        m.quad([(.294,2.683,.244),(.330,2.683,.282),
                (.408,2.683,.282),(.444,2.683,.244)],'paper',double=True)
        _front(m,.327,2.685,.271,.085,.014,'mid')
        _front(m,.317,2.685,.143,.021,.084,'mid')
        _front(m,.352,2.685,.148,.066,.041,'steel')
    elif kind=='fresh_case':
        m.quad([(.253,2.683,.119),(.274,2.683,.151),
                (.350,2.683,.281),(.379,2.683,.281),
                (.464,2.683,.147),(.481,2.683,.119)],'paper',double=True)
        _front(m,.331,2.685,.119,.072,.078,'dark')
    else:
        _front(m,.247,2.683,.126,.239,.151,'paper')
        _front(m,.258,2.685,.137,.217,.129,'dark')
        _front(m,.270,2.687,.149,.094,.105,'paper')
        _front(m,.380,2.687,.149,.080,.042,'mid')
        _front(m,.380,2.687,.208,.080,.046,'paper')
    light=m.part('case-under-canopy','cold-light')
    _top(light,.035,.12,1.848,.055,2.40,'mint')
    _west(light,.034,.12,1.82,2.40,.028,'mint')


def _freezer(m):
    _feet(m,1.6,.9,.09,.08)
    # Four walls and a low basin preserve the opening under both glass lids.
    m.box(.025,.025,.07,1.55,.055,.62,'paper',top='mid')
    m.box(.025,.82,.07,1.55,.055,.62,'paper',top='mid')
    m.box(.025,.08,.07,.055,.74,.62,'paper',top='mid')
    m.box(1.52,.08,.07,.055,.74,.62,'paper',top='mid')
    m.box(.065,.065,.63,1.47,.77,.03,'dark',top='ink')
    # Basin walls form a real opening, with food and dividers below the glass.
    m.box(.035,.03,.69,1.53,.055,.15,'mid',top='paper')
    m.box(.035,.815,.69,1.53,.055,.10,'mid',top='paper')
    for x in (.035,1.51): m.box(x,.08,.69,.055,.73,.15,'mid',top='paper')
    for x in (.12,.58,1.04):
        for y in (.15,.44):
            _bag(m,x,y,.72,.32,.23,.09,'paper' if x!=.58 else 'steel',1)
    for x in (.55,1.01): m.box(x,.10,.71,.015,.68,.10,'paper',top='white')
    # Two overlapping sliding lids, with tracks and offset handles.
    _top(m,.10,.105,.852,.72,.68,'paper',.18)
    _top(m,.78,.105,.863,.72,.68,'paper',.15)
    for x in (.10,.79,1.49): m.box(x,.105,.855,.018,.68,.025,'mid')
    for y in (.10,.78): m.box(.085,y,.85,1.43,.018,.026,'paper',top='paper')
    m.box(.68,.43,.873,.09,.16,.027,'paper',top='white')
    m.box(.84,.43,.873,.09,.16,.027,'paper',top='white')
    for row in range(3): _front(m,.13,.878,.20+row*.04,.28,.015,'steel')
    m.box(1.18,.879,.18,.24,.012,.075,'mid')
    _front(m,1.20,.893,.199,.12,.035,'dark')
    glint=m.part('freezer-lid-reflection','glass-glint')
    glint.quad([(.20,.16,.885),(.24,.16,.885),(.62,.73,.885),(.58,.73,.885)],'white',.28,double=True)
    glint.quad([(1.04,.15,.885),(1.06,.15,.885),(1.39,.65,.885),(1.37,.65,.885)],'white',.22,double=True)


def _drink_wall(m):
    # Customer doors are NORTH (-Y); the SOUTH side stays open for rear stocking.
    _feet(m,3.4,.75,.075,.075)
    m.box(.025,.035,.07,3.35,.68,.17,'steel',top='mid')
    m.box(.025,.035,1.78,3.35,.68,.12,'paper',top='paper')
    for x in (.025,3.30): m.box(x,.035,.24,.075,.68,1.54,'mid',top='paper')
    # Rear side is visibly open between narrow standards; no solid back panel.
    for x in (.095,1.16,2.23,3.29): m.box(x,.65,.24,.035,.06,1.54,'steel',top='mid')
    for z in (.25,.62,.99,1.36):
        m.box(.10,.105,z,3.20,.55,.045,'steel',top='mid')
        m.box(.10,.645,z+.017,3.20,.025,.045,'paper',top='paper')
        # Rear-stock rows expose shoulders, caps, handles and different container scales.
        for bay in range(3):
            for j in range(6):
                x=.20+bay*1.06+j*.15
                h=.27 if bay!=1 else .29
                if z==1.36 and bay==2:
                    _carton(m,x-.055,.39,z+.046,.12,.12,.27,'paper')
                elif bay==1 and z<1.0:
                    _bottle(m,x,.47,z+.046,.058,h,'steel','paper')
                else:
                    _bottle(m,x,.47,z+.046,.058,h,'paper' if (j+bay)%3 else 'mid',
                            'paper')
                # Partial front row makes the cooler useful from either side.
                if j%2==0: _bottle(m,x+.035,.24,z+.046,.052,h*.94,'mid','paper')
        for xx in (.20,.78,1.27,1.87,2.37,2.97): _tag(m,xx,.673,z+.024,'front')
    # Three framed low-E doors on the customer side; stock is visible behind them.
    for bay in range(3):
        x=.10+bay*1.06
        for xx in (x,x+1.015): m.box(xx,.035,.25,.03,.045,1.52,'paper')
        m.box(x,.035,.25,1.045,.045,.035,'mid',top='paper')
        m.box(x,.035,1.735,1.045,.045,.035,'mid',top='paper')
        _front(m,x+.035,.033,.30,.975,1.40,'paper',.08)
        m.box(x+.91,.008,.87,.028,.06,.39,'mid',top='paper')
    # A quiet status panel on the canopy, visible from the replenishment aisle.
    m.box(2.91,.717,1.81,.27,.01,.05,'dark')
    light=m.part('cooler-header-status','drink-light')
    _front(light,2.94,.729,1.825,.075,.027,'mint')
    for xx in (.12,1.18,2.24):
        # Narrow diffusers have no dark border eating their two-pixel face.
        _top(light,xx,.718,1.9,1.00,.030,'mint')
        _front(light,xx,.748,1.875,1.00,.025,'mint')


def build(model, kind):
    """Draw a standalone fixture at local NW floor origin; return its dimensions."""
    if kind == 'checkout': _checkout(model)
    elif kind == 'warmer': _warmer(model)
    elif kind == 'microwave': _microwave(model)
    elif kind == 'coffee': _coffee(model)
    elif kind == 'magazines': _magazines(model)
    elif kind.startswith('gondola_') and kind in FOOTPRINTS: _gondola(model,kind)
    elif kind in ('fresh_case','bento_case','dairy_case'): _case(model,kind)
    elif kind == 'freezer': _freezer(model)
    elif kind == 'drink_wall': _drink_wall(model)
    else: raise ValueError('Unknown shop fixture: '+str(kind))
    return FOOTPRINTS[kind]
