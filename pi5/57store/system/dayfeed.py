"""Read-only day-shift cache; no credentials, HTML execution or browser navigation."""
import base64
import json
import ssl
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

INTERVAL = 300
_LOCK = threading.Lock()
_WORKERS = {}
IMAGE_HOSTS = {'cdn.jsdelivr.net', 'raw.githubusercontent.com', 'fivsevn.com', 'fivsevn.wordpress.com'}

def now():
    return datetime.now(timezone.utc).isoformat()

def request(url, limit=3_000_000):
    context = ssl.create_default_context(cafile='/etc/ssl/cert.pem') if Path('/etc/ssl/cert.pem').exists() else ssl.create_default_context()
    req = urllib.request.Request(url, headers={'User-Agent':'57STORE-DayShift/1.0'})
    with urllib.request.urlopen(req, timeout=15, context=context) as r:
        data = r.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Response exceeds cache limit')
        return data, r.headers.get_content_type()

def api(kind, **params):
    raw, _ = request('https://fivsevn.com/wp-json/wp/v2/' + kind + '?' + urllib.parse.urlencode(params))
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError('Invalid feed response')
    return value

class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.text, self.hidden = [], [], 0
    def flush(self):
        value = ''.join(self.text).strip()
        if value: self.blocks.append({'type':'text','text':value})
        self.text = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script','style'}: self.hidden += 1
        if self.hidden: return
        if tag in {'p','div','figure','li'}: self.flush()
        if tag == 'br': self.text.append('\n')
        if tag == 'img':
            self.flush()
            url = attrs.get('src','')
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme == 'https' and parsed.hostname in IMAGE_HOSTS:
                self.blocks.append({'type':'image','url':url,'alt':attrs.get('alt','')})
    def handle_endtag(self, tag):
        if tag in {'script','style'}: self.hidden = max(0,self.hidden-1)
        if not self.hidden and tag in {'p','div','figure','li'}: self.flush()
    def handle_data(self, value):
        if not self.hidden: self.text.append(value)

class Cache:
    def __init__(self, directory):
        self.path = Path(directory)/'dayfeed.json'
        self.lock = threading.Lock()
        self.value = {'posts':[], 'foodie':[], 'sync':{'state':'waiting','last_success':None}, 'interval':INTERVAL}
        try:
            saved = json.loads(self.path.read_text())
            if isinstance(saved.get('posts'),list) and isinstance(saved.get('foodie'),list):
                self.value = saved
                self.value['sync']['state'] = 'cached'
        except (OSError, ValueError, KeyError, TypeError): pass
    def run_once(self):
        try:
            old_images = {}
            for group in ('posts','foodie'):
                for post in self.value[group]:
                    for b in post['blocks']:
                        if b['type']=='image': old_images[b['url']] = b
            result = {}
            for group in ('posts','foodie'):
                categories = api('categories', slug=group)
                category = next(c['id'] for c in categories if c['slug']==group)
                rows = api('posts',categories=category,per_page=6,orderby='date',order='desc',_fields='id,date_gmt,modified_gmt,content')
                result[group] = []
                for post in rows:
                    parser = Blocks(); parser.feed(post['content']['rendered']); parser.flush()
                    for block in parser.blocks:
                        if block['type']=='image':
                            if block['url'] in old_images: block.update(old_images[block['url']])
                            else:
                                raw, mime = request(block['url'],8_000_000)
                                if mime not in {'image/jpeg','image/png','image/webp','image/gif'}: raise ValueError('Unsupported image')
                                block['src'] = 'data:'+mime+';base64,'+base64.b64encode(raw).decode()
                    result[group].append({'id':post['id'],'date':post['date_gmt']+'Z','modified':post['modified_gmt']+'Z','blocks':parser.blocks})
            result.update(sync={'state':'online','last_success':now()},interval=INTERVAL)
            self.path.parent.mkdir(parents=True,exist_ok=True)
            temp = self.path.with_suffix('.tmp')
            temp.write_text(json.dumps(result,ensure_ascii=False));temp.replace(self.path)
            with self.lock: self.value = result
        except Exception:
            with self.lock:
                self.value = {**self.value,'sync':{**self.value['sync'],'state':'offline'}}
    def run(self):
        while True:
            self.run_once();time.sleep(INTERVAL)

def payload(directory):
    key = str(directory)
    with _LOCK:
        if key not in _WORKERS:
            cache = Cache(directory)
            _WORKERS[key] = cache
            threading.Thread(target=cache.run,name='57store-dayfeed',daemon=True).start()
        cache = _WORKERS[key]
    with cache.lock: return cache.value
