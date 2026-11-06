"""Deterministic code-only scene geometry and pixel-snapped parallel projection."""
from dataclasses import dataclass, field
from math import cos,sin,pi
from html import escape
from collections import defaultdict
import heapq

PALETTE={'ink':'#090b0c','floor':'#131415','dark':'#252a2d','steel':'#4c595e','mid':'#8a999a','paper':'#c6d0ca','white':'#edf1e7','mint':'#55efc1'}
RAMP=['ink','floor','dark','steel','mid','paper','white']
PP=78; WIDTH=672; HEIGHT=1940
VIEW=(-.025,1,.97/.79)

def project(p):
 x,y,z=p
 return (2*round((46+PP*(x+.025*y))/2),2*round((120+PP*(.97*y-.79*z))/2))

def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def shade(color,delta):
 if color=='mint':return color
 return RAMP[max(0,min(6,RAMP.index(color)+delta))]

@dataclass
class Face:
 points:list
 color:str
 opacity:float=1
 double:bool=False
 outline:bool=True

@dataclass
class Piece:
 name:str
 motion:str|None=None
 faces:list=field(default_factory=list)

class Model:
 """Local model API. Units are metres. Front is +Y, right +X, up +Z.
 box(x,y,z,width,depth,height,color) creates a shaded cuboid.
 cylinder(cx,cy,z,radius,height,color,sides=8) creates a stepped solid.
 quad(points,color,opacity=1,double=False,outline=False) draws a surface.
 part(name,motion=None) returns another local builder in this same object.
 Colors are PALETTE keys. Keep all geometry inside the stated footprint except
 natural vertical height. A fixture's local origin is its NORTH-WEST floor corner.
 """
 def __init__(self,name,x=0,y=0,rotation=0,pieces=None):
  self.name=name;self.x=x;self.y=y;self.rotation=rotation*pi/180
  self.pieces=[] if pieces is None else pieces
  self.current=Piece(name);self.pieces.append(self.current)
 def part(self,name,motion=None):
  m=Model(self.name,self.x,self.y,self.rotation*180/pi,self.pieces);m.current.name=name;m.current.motion=motion;return m
 def world(self,p):
  x,y,z=p;c=cos(self.rotation);s=sin(self.rotation)
  return (self.x+x*c-y*s,self.y+x*s+y*c,z)
 def quad(self,points,color,opacity=1,double=False,outline=False):
  if color not in PALETTE:raise ValueError('Unknown material: '+str(color))
  self.current.faces.append(Face([self.world(p) for p in points],color,opacity,double,outline))
 def box(self,x,y,z,w,d,h,color='steel',top=None):
  if min(w,d,h)<=0:raise ValueError('Geometry must have positive dimensions')
  a=(x,y,z);b=(x+w,y,z);c=(x+w,y+d,z);e=(x,y+d,z)
  A=(x,y,z+h);B=(x+w,y,z+h);C=(x+w,y+d,z+h);E=(x,y+d,z+h)
  for pts,col in [([a,e,c,b],shade(color,-1)),([A,B,C,E],top or shade(color,1)),([a,b,B,A],shade(color,-1)),([e,E,C,c],color),([a,A,E,e],shade(color,-1)),([b,c,C,B],shade(color,-1))]:
   self.quad(pts,col,outline=True)
 def cylinder(self,cx,cy,z,radius,height,color='steel',sides=8):
  low=[(cx+radius*cos(2*pi*i/sides),cy+radius*sin(2*pi*i/sides),z) for i in range(sides)]
  high=[(x,y,z+height) for x,y,_ in low]
  self.quad(high,shade(color,1),outline=True)
  for i in range(sides):
   j=(i+1)%sides;self.quad([low[i],low[j],high[j],high[i]],shade(color,0 if i<sides/2 else -1),outline=True)
 def bounds(self):
  points=[project(v) for part in self.pieces for f in part.faces for v in f.points]
  return [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)] if points else [0,0,0,0]

class Scene:
 def __init__(self):self.models=[];self.labels=[]
 def model(self,name,x,y,rotation=0):
  m=Model(name,x,y,rotation);self.models.append(m);return m
 def text(self,x,y,z,value,size=15,color='paper',anchor='start'):
  self.labels.append((project((x,y,z)),value,size,color,anchor))
 def svg(self):
  faces=[]
  for m in self.models:
   for part_index,piece in enumerate(m.pieces):
    bounds=[]
    for f in piece.faces:bounds.extend(project(v) for v in f.points)
    if not bounds:continue
    left=min(x for x,y in bounds);right=max(x for x,y in bounds)
    top=min(y for x,y in bounds);bottom=max(y for x,y in bounds)
    origin=(left if piece.motion in ('sys-type','display-scroll') else (left+right)/2,(top+bottom)/2)
    for f in piece.faces:
     n=cross(sub(f.points[1],f.points[0]),sub(f.points[2],f.points[0]))
     den=dot(n,VIEW)
     if (not f.double and den<=.000001) or abs(den)<1e-9:continue
     screen=[raw_project(v) for v in f.points]
     if abs(area(screen))<.01:continue
     faces.append({'face':f,'screen':screen,'normal':n,'den':den,'owner':m.name,'part':part_index,'piece':piece,'origin':origin,'box':bounds2(screen)})
  out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" class="room-art" aria-hidden="true" shape-rendering="crispEdges">']
  previous=None;first=set()
  for index in paint_order(faces):
   item=faces[index];key=(item['owner'],item['part'])
   if key!=previous:
    if previous is not None:out.append('</g>')
    piece=item['piece'];owner=escape(item['owner']);cls='world-object piece'+(' motion '+piece.motion if piece.motion else '')
    ident=f' id="object-{owner}"' if owner not in first else ''
    first.add(owner)
    ox,oy=item['origin'];sty=f' style="transform-box:view-box;transform-origin:{ox:g}px {oy:g}px"' if piece.motion else ''
    out.append(f'<g{ident} data-owner="{owner}" data-piece="{escape(piece.name)}" class="{escape(cls)}"{sty}>');previous=key
   f=item['face'];points=' '.join(f'{x},{y}' for x,y in [project(v) for v in f.points])
   stroke=' stroke="#090b0c" stroke-width="1.5" stroke-linejoin="miter"' if f.outline else ''
   op=f' opacity="{f.opacity:g}"' if f.opacity!=1 else ''
   out.append(f'<polygon points="{points}" fill="{PALETTE[f.color]}"{stroke}{op}/>')
  if previous is not None:out.append('</g>')
  for (x,y),value,size,color,anchor in self.labels:
   out.append(f'<text x="{x}" y="{y}" fill="{PALETTE[color]}" font-family="RoomMono,monospace" font-size="{size}" text-anchor="{anchor}" shape-rendering="auto">{escape(value)}</text>')
  out.append('</svg>');return ''.join(out)


def raw_project(p):
 x,y,z=p
 return (46+PP*(x+.025*y),120+PP*(.97*y-.79*z))

def bounds2(poly):return (min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly))
def area(poly):return sum(poly[i-1][0]*p[1]-p[0]*poly[i-1][1] for i,p in enumerate(poly))/2

def intersection(subject,clip):
 """Convex projected-face intersection, used only for ordering, not drawing."""
 orient=1 if area(clip)>0 else -1
 def side(a,b,p):return orient*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
 for i,b in enumerate(clip):
  a=clip[i-1];source=subject;subject=[]
  if not source:return []
  start=source[-1];ds=side(a,b,start)
  for end in source:
   de=side(a,b,end)
   if (ds>=-1e-7)!=(de>=-1e-7):
    ratio=ds/(ds-de)
    subject.append((start[0]+ratio*(end[0]-start[0]),start[1]+ratio*(end[1]-start[1])))
   if de>=-1e-7:subject.append(end)
   start=end;ds=de
 return subject

def ray_depth(item,x,y):
 n=item['normal'];u=(x-46)/PP;v=(y-120)/PP
 return (dot(n,item['face'].points[0])-n[0]*u+n[2]*v/.79)/item['den']

def paint_order(items):
 """Order overlapping faces by depth on their shared screen ray.

 Centroid sorting is insufficient for long shelf planes and small label planes.
 A spatial grid limits pair comparisons, then a stable topological order places
 each occluder after the face behind it. All source geometry stays vector.
 """
 n=len(items);grid=defaultdict(list);pairs=set()
 for i,item in enumerate(items):
  l,t,r,b=item['box']
  for gx in range(int(l//48),int(r//48)+1):
   for gy in range(int(t//48),int(b//48)+1):
    bucket=grid[gx,gy]
    for j in bucket:pairs.add((j,i))
    bucket.append(i)
 links=[set() for _ in items];degree=[0]*n;hidden=set()
 for a,b in sorted(pairs):
  A=items[a];B=items[b];al,at,ar,ab=A['box'];bl,bt,br,bb=B['box']
  if min(ar,br)-max(al,bl)<.02 or min(ab,bb)-max(at,bt)<.02:continue
  overlap=intersection(A['screen'],B['screen'])
  if len(overlap)<3 or abs(area(overlap))<.02:continue
  x=sum(p[0] for p in overlap)/len(overlap);y=sum(p[1] for p in overlap)/len(overlap)
  difference=ray_depth(A,x,y)-ray_depth(B,x,y)
  behind,front=(a,b) if difference<=1e-7 else (b,a)
  if front not in links[behind]:links[behind].add(front);degree[front]+=1
  # Do not ship faces completely concealed by a stationary opaque surface.
  # Keep dynamic occluders and partially visible boundaries intact.
  rear=items[behind];near=items[front]
  if near['face'].opacity==1 and not near['piece'].motion:
   rl,rt,rr,rb=rear['box'];nl,nt,nr,nb=near['box']
   if nl<=rl and nt<=rt and nr>=rr and nb>=rb:
    orientation=1 if area(near['screen'])>0 else -1
    inside=all(orientation*((q[0]-p[0])*(v[1]-p[1])-(q[1]-p[1])*(v[0]-p[0]))>=.6*((q[0]-p[0])**2+(q[1]-p[1])**2)**.5 for p,q in zip(near['screen'][-1:]+near['screen'][:-1],near['screen']) for v in rear['screen'])
    if inside and all(ray_depth(near,*v)>=ray_depth(rear,*v)+1e-6 for v in rear['screen']):hidden.add(behind)
 heap=[]
 def distance(i):
  f=items[i]['face'];return sum(dot(p,VIEW) for p in f.points)/len(f.points)
 for i in range(n):
  if not degree[i]:heapq.heappush(heap,(distance(i),i))
 result=[];done=set()
 while heap:
  _,i=heapq.heappop(heap)
  if i in done:continue
  done.add(i);result.append(i)
  for j in sorted(links[i]):
   degree[j]-=1
   if degree[j]==0:heapq.heappush(heap,(distance(j),j))
 # Physically intersecting construction solids can make a tiny local cycle;
 # preserve a deterministic order there while keeping all acyclic constraints.
 while len(done)<n:
  # Release only the earliest blocked face when intersecting construction
  # pieces form a cycle, then continue honoring every remaining dependency.
  i=min((i for i in range(n) if i not in done),key=lambda i:(distance(i),i))
  heapq.heappush(heap,(distance(i),i))
  while heap:
   _,j=heapq.heappop(heap)
   if j in done:continue
   done.add(j);result.append(j)
   for k in sorted(links[j]):
    degree[k]-=1
    if degree[k]==0:heapq.heappush(heap,(distance(k),k))
 return [i for i in result if i not in hidden]
