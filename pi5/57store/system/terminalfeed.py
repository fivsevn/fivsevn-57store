"""Local, persistent Signal and weather delivery for the store terminal."""
import json,ssl,threading,time,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime,timezone
SIGNAL_URL='https://devlog.fivsevn.com/now/'
WEATHER_URL='https://api.open-meteo.com/v1/forecast?latitude=32.02&longitude=120.86&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=ms&timezone=Asia%2FShanghai'
class Signal(HTMLParser):
 def __init__(self):
  super().__init__();self.active=False;self.capture=None;self.parts=[];self.entries=[];self.date='';self.hidden=0
 def handle_starttag(self,t,a):
  attrs=dict(a)
  if t in ['h1','h2','h3','h4','hr','details']:
   self.active=t.startswith('h') and attrs.get('id','').lower().strip('-')=='signal'
  if not self.active:return
  if t in ['script','style']:self.hidden+=1
  if t in ['li','code'] and not self.hidden:self.capture=t;self.parts=[]
  if t=='br' and self.capture:self.parts.append('\n')
 def handle_data(self,s):
  if self.active and self.capture and not self.hidden:self.parts.append(s)
 def handle_endtag(self,t):
  if t in ['script','style']:self.hidden=max(0,self.hidden-1)
  if t==self.capture:
   value=''.join(self.parts).strip()
   if t=='li' and value:self.entries.append(value)
   if t=='code' and value:self.date=value
   self.capture=None
 def result(self):
  if not self.entries:raise ValueError('No Signal found')
  return {'text':self.entries[-1],'date':self.date}
def fetch(kind):
 context=ssl.create_default_context(cafile='/etc/ssl/cert.pem') if Path('/etc/ssl/cert.pem').exists() else ssl.create_default_context()
 req=urllib.request.Request(SIGNAL_URL if kind=='signal' else WEATHER_URL,headers={'User-Agent':'57STORE-Terminal/1.0'})
 with urllib.request.urlopen(req,timeout=15,context=context) as r:
  raw=r.read(1_000_001)
  if len(raw)>1_000_000:raise ValueError('Response too large')
 if kind=='signal':
  parser=Signal();parser.feed(raw.decode('utf-8'));return parser.result()
 result=json.loads(raw)
 if not isinstance(result.get('current'),dict) or result['current'].get('temperature_2m') is None:raise ValueError('Invalid weather')
 return result
class Cache:
 def __init__(self,directory,kind):
  self.kind=kind;self.path=Path(directory)/(kind+'.json');self.lock=threading.Lock();self.data={'value':None,'state':'waiting','received_at':None}
  try:
   self.data=json.loads(self.path.read_text());self.data['state']='cached'
  except (OSError,ValueError):pass
 def once(self):
  try:
   result={'value':fetch(self.kind),'state':'online','received_at':datetime.now(timezone.utc).isoformat()}
   self.path.parent.mkdir(parents=True,exist_ok=True);tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False));tmp.replace(self.path)
   with self.lock:self.data=result
  except Exception:
   with self.lock:self.data={**self.data,'state':'offline'}
 def run(self):
  while True:self.once();time.sleep(300 if self.kind=='signal' else 900)
_lock=threading.Lock();_caches={}
def payload(directory,kind):
 assert kind in ('signal','weather')
 with _lock:
  key=(str(directory),kind)
  if key not in _caches:
   c=Cache(directory,kind);_caches[key]=c;threading.Thread(target=c.run,daemon=True).start()
  c=_caches[key]
 with c.lock:return c.data
