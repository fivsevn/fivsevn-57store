"""Original arrangement in metre space; all fixtures share one projection."""
from pathlib import Path
import runpy

HERE=Path(__file__).parent

# The rear rooms move together as the three-row sales floor becomes shorter.
REAR_Y=15.4
STORE_END=REAR_Y+6.0
# These are physical areas, not the visible pixel silhouettes of raised objects.
ROOMS={'sales':(.25,.45,6.7,REAR_Y-.65),'toilet':(.25,REAR_Y,2.15,2.8),'cold':(3.5,REAR_Y+.8,3.45,2.0),'staff':(.25,REAR_Y+2.9,6.7,3.0)}


def assemble(Scene):
    shop=runpy.run_path(str(HERE/'shop.py'))['build']
    back=runpy.run_path(str(HERE/'back.py'))['build']
    s=Scene();items=[]
    def surface(m,points,c='ink',opacity=1):m.quad(points,c,opacity=opacity,double=True)
    def place(ident,kind,x,y,label,note,area,*,rear=False,rotation=0,href=None,target=None):
        m=s.model(ident,x,y,rotation)
        w,d=area
        surface(m,[(.08,.12,.015),(w+.17,.12,.015),(w+.17,d+.22,.015),(.08,d+.22,.015)],'ink',.62)
        back(m,kind,coat='mint' if ident in ('clerk','restocker') else 'steel') if rear else shop(m,kind)
        items.append(dict(id=ident,label=label,note=note,href=href,model=m,target=target,footprint=(x,y,w,d)))
        return m
    def bare(ident,x,y,label,note,area,target=None):
        m=s.model(ident,x,y);items.append(dict(id=ident,label=label,note=note,href=None,model=m,target=target,footprint=(x,y,*area)));return m
    # Dark inset floor and low cut-away walls: the whole visible experience is interior.
    floor=s.model('ground',0,0)
    floor.box(.14,.14,-.13,6.95,STORE_END-.02,.13,'dark',top='floor')
    for x in [i*.60+.18 for i in range(12)]:floor.quad([(x,.2,.005),(x+.008,.2,.005),(x+.008,STORE_END,.005),(x,STORE_END,.005)],'dark',outline=False)
    for n in range(int((STORE_END-.2)/.6)+1):
        y=.2+n*.60;floor.quad([(.2,y,.006),(7.0,y,.006),(7.0,y+.008,.006),(.2,y+.008,.006)],'dark')
    # West/east wall caps have thickness and a darker skirting, rather than an outline box.
    walls=s.model('shell',0,0)
    for x in (.13,7.0):
        walls.box(x,.12,0,.12,STORE_END,.36,'dark',top='steel')
        walls.box(x+.03,.15,.36,.055,STORE_END-.08,.045,'mid')
    walls.box(.13,STORE_END,0,6.99,.13,.24,'dark',top='steel')
    # Entrance glazing. Central sliding leaves are moving geometry, not a UI frame.
    front=bare('entrance',.25,.35,'自动门','雨停后，门还会开。',(6.7,.2),target=(3.5,.40,.8,150,110))
    for x,w in ((0,2.7),(4.35,2.4)):
        front.box(x,0,0,w,.12,1.65,'dark')
        surface(front,[(x+.06,.125,.16),(x+w-.06,.125,.16),(x+w-.06,.125,1.55),(x+.06,.125,1.55)],'steel',.25)
        for h in (.08,.82,1.56):front.box(x,.10,h,w,.045,.035,'mid')
        for xx in (x,x+w/2,x+w-.04):front.box(xx,.10,.05,.035,.05,1.55,'steel')
    for name,x in (('door-l',2.72),('door-r',3.53)):
        p=front.part(name,name);p.box(x,.02,.03,.79,.1,1.58,'dark')
        p.quad([(x+.04,.125,.14),(x+.74,.125,.14),(x+.74,.125,1.52),(x+.04,.125,1.52)],'steel',opacity=.24,double=True)
        for z in (.12,.83,1.52):p.box(x+.02,.13,z,.75,.035,.025,'paper')
        p.quad([(x+.06,.18,.83),(x+.72,.18,.83),(x+.72,.18,.88),(x+.06,.18,.88)],'mint',double=True)
    front.box(2.68,-.02,1.63,1.67,.2,.16,'dark');front.part('door-sensor','sensor').quad([(3.42,.19,1.67),(3.58,.19,1.67),(3.58,.19,1.72),(3.42,.19,1.72)],'mint',double=True)
    # A woven physical mat carries the only large textual branding.
    mat=bare('mat',2.45,1.04,'入口地毯','每日生活，本地缓存。',(2.75,1.3),target=(3.8,1.80,.02,180,96))
    mat.box(0,0,.012,2.75,1.32,.025,'dark')
    for y in (.08,1.24):mat.box(.07,y,.04,2.61,.016,.012,'steel')
    s.text(3.82,1.22,.055,'57STORE',24,'mint','middle')
    s.text(3.82,1.48,.055,'ゴナナストア',12,'paper','middle')
    s.text(3.82,1.75,.055,'每日生活、本地缓存。',13,'white','middle')
    s.text(3.82,1.98,.055,'Daily Life, Local Cache.',12,'paper','middle')
    s.text(3.82,2.20,.055,'暮らし、ローカルキャッシュ。',12,'paper','middle')
    # Checkout stands beside the entrance with an actual staff working aisle.
    workwall=s.model('checkout-back',.27,1.37);workwall.box(0,0,0,2.38,.13,1.15,'dark')
    place('hotcase','warmer',.35,1.66,'热食柜','炸鸡与可乐饼还热着。',(1,.6))
    place('microwave','microwave',1.55,1.66,'微波炉','便当加热，稍等一会。',(.85,.65))
    place('clerk','human',.95,2.48,'夜班店员','正在核对上一笔交易。',(.45,.4),rear=True,target=(1.15,2.62,1.25,68,72))
    place('receipt','checkout',.35,3.38,'小票打印机','纸卷装好了。',(2,.85),href='/receipt/',target=(1.35,3.95,.95,180,124))
    place('magazines','magazines',6.34,1.10,'杂志架','城市、旅行、漫画。',(.6,1.7))
    place('baskets','baskets',5.03,2.85,'购物篮','空篮放回这一叠。',(.55,.45),rear=True)
    place('umbrellas','umbrella',6.30,3.40,'伞架','伞尖的水还没有干。',(.55,.45),rear=True)
    place('coffee','coffee',.35,5.12,'咖啡机','豆仓、磨豆声与热蒸汽。',(1,.8))
    place('freezer','freezer',3.77,4.20,'冰淇淋柜','玻璃滑盖下是冰品。',(1.6,.9))
    # Public aisles run continuously around three islands.
    place('snacks','gondola_snacks',4.90,6.45,'零食货架','薯片、仙贝、分享装。',(1.05,3.0),rotation=90)
    place('noodles','gondola_noodles',4.90,8.85,'速食货架','杯面、即食汤与罐头。',(1.05,3.0),rotation=90)
    place('bread','gondola_bread',4.90,11.25,'面包货架','吐司、餐包与小点心。',(1.05,3.0),rotation=90)
    place('dairy','dairy_case',6.16,5.20,'乳品冷柜','牛奶、酸奶与布丁。',(.75,2.7))
    place('fresh','fresh_case',6.16,8.55,'鲜食冷柜','饭团和三明治。',(.75,2.7))
    place('bento','bento_case',6.16,11.90,'便当冷柜','便当、沙拉与冷面。',(.75,2.7))
    # Small wall-side recycling and a low daily-goods display keep left aisle open.
    bins=bare('recycling',.33,7.45,'分类回收','空罐和空瓶分开放。',(.55,1.28))
    for y in (0,.70):
        bins.box(0,y,0,.5,.55,.82,'steel');bins.box(.05,y+.06,.83,.4,.43,.045,'paper')
        bins.quad([(.14,y+.16,.881),(.36,y+.16,.881),(.36,y+.35,.881),(.14,y+.35,.881)],'ink',double=True)
        bins.box(.12,y+.552,.46,.28,.008,.16,'dark')
    low=bare('delivery-display',.33,10.10,'日用品端架','纸巾、电池与清洁用品。',(1.0,.75))
    low.box(0,0,.05,.95,.7,.75,'steel');low.box(.03,.03,.82,.89,.64,.04,'mid')
    low.box(.08,.13,.87,.34,.29,.22,'paper')
    low.box(.16,.22,1.092,.17,.06,.012,'dark')
    low.quad([(.20,.23,1.11),(.29,.23,1.11),(.31,.26,1.20),(.23,.29,1.18)],'white',double=True)
    low.box(.47,.16,.87,.13,.25,.28,'mid')
    for x in (.49,.55):
        low.cylinder(x,.405,.92,.020,.14,'paper')
        low.box(x-.018,.427,1.02,.036,.008,.02,'dark')
    low.cylinder(.78,.35,.87,.085,.25,'paper')
    low.cylinder(.78,.35,1.12,.038,.08,'steel')
    low.box(.755,.33,1.20,.11,.04,.028,'mid')
    place('customer','human',1.18,10.93,'顾客','拿着篮子，慢慢挑选。',(.45,.4),rear=True,target=(1.39,11.13,1.1,70,94))
    place('reader','human',5.73,2.40,'翻杂志的顾客','还没决定要带走哪一本。',(.45,.4),rear=True,rotation=-90,target=(5.95,2.10,1.1,66,90))
    # Camera is visibly a small camera, not a large clickable monitor panel.
    cam=bare('camera',6.6,.72,'入口摄像头','记录门口的来往。',(.35,.25))
    cam.box(.15,.05,1.55,.035,.06,.35,'steel');c=cam.part('camera-head','camera-turn')
    c.box(0,0,1.50,.29,.24,.16,'paper')
    from math import cos,sin,pi
    c.quad([(.14+.078*cos(2*pi*i/8),.246,1.58+.065*sin(2*pi*i/8)) for i in range(8)],'steel',double=True)
    c.quad([(.14+.052*cos(2*pi*i/8),.250,1.58+.045*sin(2*pi*i/8)) for i in range(8)],'ink',double=True)
    # Toilet and employee access are distinct doors off the PUBLIC rear aisle.
    wc=s.model('wc-room',.25,REAR_Y-.02)
    wc.box(0,0,0,1.15,.13,1.35,'dark');wc.box(2.05,0,0,.10,.13,1.35,'dark')
    wc.box(2.10,0,0,.10,2.88,.65,'dark');wc.box(0,2.80,0,2.20,.13,.7,'dark')
    for x in (.08,.65,1.22,1.79):wc.box(x,.15,.01,.012,2.60,.006,'steel')
    for y in (.16,.73,1.30,1.87,2.44):wc.box(.06,y,.011,2.03,.012,.006,'steel')
    door=bare('wc-door',1.42,REAR_Y-.02,'厕所门','从卖场公共通道进入。',(.92,.13))
    door.box(0,0,0,.055,.16,1.72,'steel');door.box(.87,0,0,.055,.16,1.72,'steel');door.box(0,0,1.67,.92,.16,.07,'mid')
    door.box(.84,.12,0,.065,.86,1.60,'mid');door.box(.83,.72,.79,.04,.07,.035,'mint')
    place('toilet','toilet',.54,REAR_Y+.12,'坐便器','水箱靠墙，纸架在侧边。',(.8,1.1),rear=True)
    place('basin','wall_basin',2.34,REAR_Y+1.72,'洗手盆','皂液和镜子都在墙边。',(.65,.5),rear=True,rotation=90)
    paper=bare('wc-paper',.28,REAR_Y+.62,'厕纸架','纸卷固定在侧墙。',(.22,.28))
    paper.box(0,0,.77,.12,.25,.06,'steel')
    from math import cos,sin,pi
    rings=[[(.14+.075*cos(2*pi*i/8),y,.68+.075*sin(2*pi*i/8)) for i in range(8)] for y in (.03,.20)]
    for i in range(8):
        j=(i+1)%8;paper.quad([rings[0][i],rings[1][i],rings[1][j],rings[0][j]],'paper',double=True)
    paper.quad(rings[1],'white',double=True)
    paper.quad([(.14+.025*cos(2*pi*i/8),.201,.68+.025*sin(2*pi*i/8)) for i in range(8)],'dark',double=True)
    paper.quad([(.21,.04,.68),(.21,.19,.68),(.21,.19,.48),(.21,.04,.48)],'white',double=True)
    # Walk-in is a real service volume behind the drink display, not every cold case.
    place('drinks','drink_wall',3.50,REAR_Y,'饮料冷柜','顾客取货，后面补货。',(3.4,.75))
    cold=s.model('cold-room',3.45,REAR_Y+.75)
    cold.box(0,0,0,.12,.72,.85,'dark');cold.box(0,1.62,0,.12,.43,.85,'dark')
    cold.box(.0,2.05,0,3.5,.13,.85,'dark')
    for y in (.08,.68,1.28,1.88):cold.box(.14,y,.01,3.25,.012,.008,'steel')
    coldDoor=bare('cold-door',3.46,REAR_Y+1.47,'冷藏间保温门','补货从员工侧进入。',(.12,.92))
    coldDoor.box(.02,0,0,.12,.06,1.78,'mid');coldDoor.box(.02,.85,0,.12,.06,1.78,'mid');coldDoor.box(.02,0,1.72,.12,.91,.06,'paper')
    coldDoor.box(.14,.78,.04,.78,.08,1.61,'mid');coldDoor.box(.19,.868,.14,.67,.012,1.41,'paper')
    coldDoor.box(.77,.88,.74,.04,.035,.22,'steel')
    for z in (.18,1.44):coldDoor.box(.14,.875,z,.06,.025,.11,'steel')
    place('chilled-stock','stockrack',5.42,REAR_Y+2.09,'预冷库存','整箱饮料在这里预冷。',(1.4,.55),rear=True)
    place('restocker','human',4.63,REAR_Y+1.96,'补货店员','把新货放到货道后面。',(.45,.4),rear=True,rotation=180)
    fan=bare('fan',6.28,REAR_Y+1.05,'冷库风机','空气在狭窄货道里循环。',(.5,.3))
    fan.box(0,0,1.70,.46,.24,.28,'steel');fan.quad([(.04,.245,1.74),(.42,.245,1.74),(.42,.245,1.94),(.04,.245,1.94)],'ink',double=True)
    f=fan.part('fan-blades','fan-spin');f.quad([(.20,.25,1.74),(.26,.25,1.74),(.26,.25,1.94),(.20,.25,1.94)],'paper',double=True)
    f.quad([(.09,.25,1.81),(.37,.25,1.81),(.37,.25,1.87),(.09,.25,1.87)],'paper',double=True)
    # Only one compact staff room. A straight entrance separates the single desk and the locker wall.
    staff=s.model('staff-room',.25,REAR_Y+2.90)
    staff.box(0,0,0,2.13,.12,1.25,'dark');staff.box(3.18,0,0,3.55,.12,1.25,'dark')
    entrance=bare('staff-door',2.42,REAR_Y,'员工门','内部工作区。',(.93,.14))
    entrance.box(0,0,0,.07,.16,1.75,'steel');entrance.box(.87,0,0,.07,.16,1.75,'steel');entrance.box(0,0,1.69,.94,.16,.07,'mid')
    entrance.box(.85,.12,.03,.07,.82,1.59,'dark');entrance.box(.84,.70,.84,.04,.07,.035,'mint')
    place('sys','sys_desk',.43,REAR_Y+3.07,'店务终端','内部系统，等待操作。',(1.65,1.45),rear=True,href='/sys/',target=(1.28,REAR_Y+3.55,1.16,138,140))
    for index,x in enumerate((4.01,5.00,5.99),1):
        place(f'lockers-{index}','lockers',x,REAR_Y+3.00,f'员工储物柜 {index:02d}','六格独立柜，放制服与私人物品。',(1,.5),rear=True)
    place('stock','stockrack',.36,REAR_Y+5.72,'后场库存','箱子沿墙码好，通道留空。',(1.4,.55),rear=True,rotation=-90)
    place('cart','cart',1.32,REAR_Y+5.15,'收货推车','等待核对的纸箱。',(.8,.55),rear=True)
    place('utility','utility',6.94,REAR_Y+4.65,'工作水槽','器具清洗与简单备餐。',(.9,.7),rear=True,rotation=90)
    place('tea','tea_counter',3.77,REAR_Y+5.83,'茶水角','热水、杯子与一小段休息。',(1.1,.55),rear=True,rotation=180)
    place('stool','stool',3.85,REAR_Y+4.78,'折凳','交班前坐一会。',(.45,.45),rear=True)
    return s,items
