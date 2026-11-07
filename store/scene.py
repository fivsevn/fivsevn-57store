"""Render the standalone room and semantic controls from fresh scene geometry."""
from pathlib import Path
from html import escape
import runpy

HERE=Path(__file__).parent


def render():
    engine=runpy.run_path(str(HERE/'mesh.py'))
    Scene,project=engine['Scene'],engine['project']
    W,H=engine['WIDTH'],engine['HEIGHT']
    assemble=runpy.run_path(str(HERE/'plan.py'))['assemble']
    scene,items=assemble(Scene)
    controls=[]
    for item in items:
        if item['target']:
            x,y,z,w,h=item['target'];cx,cy=project((x,y,z))
        else:
            # Cover the whole visible fixture: the upper and lower shelves
            # must respond to the same tap as its middle, without a hover cue.
            x1,y1,x2,y2=item['model'].bounds();cx=(x1+x2)/2;cy=(y1+y2)/2
            w=max(76,x2-x1);h=max(76,y2-y1)
        if item['href']:w=max(116,w);h=max(116,h)
        left=max(2,min(W-w-2,cx-w/2));top=max(2,min(H-h-2,cy-h/2))
        style=f'left:{left/W*100:.5f}%;top:{top/H*100:.5f}%;width:{w/W*100:.5f}%;height:{h/H*100:.5f}%'
        common=f'class="room-control" data-object="{item["id"]}" style="{style}" aria-label="{escape(item["label"])}"'
        if item['href']:
            controls.append(f'<a {common} href="{item["href"]}"><span class="sr-only">{escape(item["label"])}</span></a>')
        else:
            controls.append(f'<button {common} type="button" data-note-title="{escape(item["label"])}" data-note="{escape(item["note"])}" aria-expanded="false" aria-controls="room-note" hidden><span class="sr-only">{escape(item["label"])}</span></button>')
    controls.append('<aside id="room-note" class="room-note" role="status" hidden><strong></strong><span></span></aside>')
    description='57store 夜班便利店。入口在画面上方，收银台邻近门口，三座中央双面货架两侧保留顾客通道，冷柜沿外围布置。后侧公共过道分别进入厕所和员工门；厕所水箱靠墙、门与洗手位错开。饮料柜背后是有独立保温门的补货冷藏间。末端仅有一个紧凑员工区，左侧店务电脑直接进入 SYS，再由 SYS 进入 CCTV；右侧为整排员工储物柜。桌柜靠墙、操作面朝通路。点按物件可看简短说明。'
    return {'svg':scene.svg(),'controls':''.join(controls),'description':description}
