#!/usr/bin/env python3
"""Build the 57store narrative site from local sources without network access."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import shutil
import subprocess
from urllib.parse import quote, urlsplit, urlunsplit
from zoneinfo import ZoneInfo
import markdown
from bs4 import BeautifulSoup
from site_post_metadata import read_frontmatter, validate_metadata, published_datetime, is_published
from head_metadata import compact_text, metadata_head, add_missing_metadata

SITE_URL = 'https://57store.fivsevn.com'
DESCRIPTIONS = {
    'home':'五月七日便利店，保存日志、影像与片段的叙事空间。',
    'receipt':'Receipt · 五月七日便利店的小票与店务记录。',
    'sys':'SYS · 五月七日便利店的系统日志。',
    'cctv':'CCTV · 五月七日便利店的影像记录。',
    'cache':'.cache · 五月七日便利店的连续对话与留存片段。',
    'fragment':'Fragment · 五月七日便利店的片段记录。',
}

ROOT = Path(__file__).resolve().parents[1]
SIZES = {'sys': 15, 'cctv': 17}
IMAGE_EXTENSIONS = {'.jpg','.jpeg','.png','.webp','.gif','.avif','.svg','.bmp','.ico','.heic','.heif','.tif','.tiff'}
RUNTIME_EXTENSIONS = IMAGE_EXTENSIONS | {'.html','.css','.js','.json','.woff','.woff2','.ttf','.otf','.txt'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def store_revisions(root):
    root=Path(root).resolve()
    def git(*args):
        try:
            return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,text=True).stdout.strip()
        except subprocess.CalledProcessError as error:
            raise ValueError('Store statistics require a Git checkout with committed history') from error
    if Path(git('rev-parse','--show-toplevel')).resolve()!=root:
        raise ValueError('Store statistics must use this repository, not a parent checkout')
    if git('rev-parse','--is-shallow-repository')=='true':
        raise ValueError('Store statistics require complete history; run git fetch --unshallow')
    return int(git('rev-list','--count','HEAD'))


def base_prefix(value):
    value = '/' + value.strip('/') if value.strip('/') else ''
    if '\\' in value or '?' in value or '#' in value or any(part in {'.','..'} for part in value.split('/')):
        raise ValueError('Invalid base path')
    return value


def prefixed(value, base):
    if value.startswith('/') and not value.startswith('//') and base and not (value == base or value.startswith(base + '/')):
        return base + value
    return value


def rewrite_css(text, base):
    return re.sub(r'url\(\s*([\'"]?)(.*?)\1\s*\)', lambda m: 'url(' + m[1] + prefixed(m[2], base) + m[1] + ')', text, flags=re.S)


def safe_asset(package, relative):
    if not isinstance(relative,str) or '\\' in relative or '\x00' in relative:
        raise ValueError('Unsafe package asset')
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts or path.as_posix()!=relative or len(path.parts)<2 or path.parts[0]!='assets':
        raise ValueError('Package assets must stay inside assets/')
    result = package.joinpath(*path.parts)
    if not result.is_file() or any(p.is_symlink() for p in [result,*result.parents] if p.is_relative_to(package)):
        raise ValueError('Missing or symlinked package asset: ' + relative)
    if result.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError('Unsupported package image: ' + relative)
    return result


def load_posts(root=ROOT):
    root=Path(root);result={};manifest=root/'site-data/content.json'
    retained=json.loads(manifest.read_text()).get('retained_posts',{}) if manifest.exists() else {}
    for board in ('sys','cctv'):
        items=[];ids=set();videos=set();rank={ident:n for n,ident in enumerate(retained.get(board,[]))}
        for source in sorted((root/board).glob('*/*/*/index.md')):
            if any(p.is_symlink() for p in [source,*source.parents] if p.is_relative_to(root/board)):
                raise ValueError('Symlinked post package')
            meta,body=read_frontmatter(source)
            validate_metadata(meta,site=board,schema_dir=root/'schemas')
            instant=published_datetime(meta)
            local=instant.astimezone(ZoneInfo('Asia/Shanghai'))
            if source.parent.name!=meta['id'] or source.parent.parent.name!=local.strftime('%m') or source.parent.parent.parent.name!=local.strftime('%Y'):
                raise ValueError('Post ID/date does not match its package: '+str(source))
            if meta['id'] in ids:raise ValueError('Duplicate package ID: '+meta['id'])
            if board=='cctv':
                for video in meta['extra']['video_ids']:
                    if video in videos:raise ValueError('Duplicate CCTV video ID: '+video)
                    videos.add(video)
            ids.add(meta['id']);items.append({'meta':meta,'body':body,'path':source,'datetime':local})
        result[board]=sorted(items,key=lambda p:(p['datetime'],-rank.get(p['meta']['id'],len(rank)),p['meta']['id']),reverse=True)
    return result


def render_body(post, board):
    package=post['path'].parent
    extensions=['tables','fenced_code','sane_lists']+(['nl2br'] if board=='sys' else [])
    rendered=markdown.markdown(post['body'],extensions=extensions)
    soup=BeautifulSoup(rendered,'html.parser')
    for el in soup.select('script,style,object,embed,iframe,form,input,button'):el.decompose()
    for el in soup.find_all():
        for attr in list(el.attrs):
            if attr.startswith('on'):del el[attr]
        for attr in ('href','src'):
            value=el.get(attr)
            if not value:continue
            parsed=urlsplit(value)
            if parsed.scheme and parsed.scheme not in {'https','http','mailto','tel'}:del el[attr];continue
            if parsed.path.startswith('assets/'):
                safe_asset(package,parsed.path)
                el[attr]=f"/{board}/{post['meta']['id']}/{value}"
            elif attr=='src' and not value.startswith('/site-assets/'):
                raise ValueError('Post images must use package assets or shared site-assets')
    extra=post['meta'].get('extra',{})
    if extra.get('image'):
        original=safe_asset(package,extra['image']);src=f"/{board}/{post['meta']['id']}/{extra['image']}"
        if not soup.find('img',src=src):
            figure=soup.new_tag('figure');picture=soup.new_tag('img',attrs={'src':src,'alt':extra.get('alt',''),'loading':'lazy'})
            figure.append(picture);soup.insert(0,figure)
    return str(soup)


def render_store(root):
    """Fill the store's body fragment with its deterministic local scene."""
    root=Path(root)
    renderer=runpy.run_path(str(root/'store/scene.py')).get('render')
    if not callable(renderer):raise ValueError('Store scene needs a render() function')
    scene=renderer()
    if not isinstance(scene,dict) or any(not isinstance(scene.get(key),str) for key in ('svg','controls','description')):
        raise ValueError('Store render() must return svg, controls and description strings')
    source=(root/'store/page.html').read_text()
    for key in ('svg','controls','description'):
        slot='{{scene_'+key+'}}'
        if source.count(slot)!=1:raise ValueError('Store page needs one scene slot: '+key)
        source=source.replace(slot,html.escape(scene[key]) if key=='description' else scene[key])
    if re.search(r'{{\s*scene_',source):raise ValueError('Unknown store scene slot')
    return BeautifulSoup(source,'html.parser')


def build(root=ROOT, output=None, base_path=''):
    root=Path(root).resolve();out=Path(output) if output else root/'_site'
    if not out.is_absolute():out=root/out
    out=out.resolve();base=base_prefix(base_path)
    if out==root or root.is_relative_to(out):raise ValueError('Unsafe output path')
    if out.is_relative_to(root) and out.relative_to(root).parts[0] in {'store','receipt','sys','cctv','cache','fragment','toilet','pi5','site-assets','site-data','scripts','templates','schemas','tests','.git'}:
        raise ValueError('Output overlaps a source directory')
    home=render_store(root)
    posts=load_posts(root)
    public={board:[p for p in values if is_published(p['meta'])] for board,values in posts.items()}
    stats={'revisions':store_revisions(root),'receipts':sum(len(values) for values in public.values())}
    cache=json.loads((root/'cache/posts.json').read_text())
    cache.sort(key=lambda p:datetime.fromisoformat(p['published_at']))
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)
    def copy_runtime(source,dest):
        if not source.exists():return
        for path in sorted(source.rglob('*')):
            relative=path.relative_to(source)
            if any(part.startswith('.') for part in relative.parts):continue
            if path.is_symlink():raise ValueError('Symlink runtime resource: '+str(path))
            if path.is_file() and path.suffix.lower() in RUNTIME_EXTENSIONS:
                target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True)
                if path.suffix.lower()=='.css' and base:target.write_text(rewrite_css(path.read_text(),base))
                elif path.suffix.lower()=='.html' and (base or source==root/'pi5/57store/system/static'):
                    content=path.read_text()
                    if source==root/'pi5/57store/system/static':
                        content=re.sub(r'([\'"])/static/',r'\1/pi5/57store/system/static/',content)
                    if base:
                        document=BeautifulSoup(content,'html.parser')
                        for el in document.find_all():
                            for attr in ('href','src','poster'):
                                if el.get(attr):el[attr]=prefixed(el[attr],base)
                        content=str(document)
                    target.write_text(content)
                else:shutil.copyfile(path,target)
    copy_runtime(root/'site-assets',out/'site-assets')
    for module in ('store','receipt','cache','fragment','sys','cctv'):
        copy_runtime(root/module/'assets',out/module/'assets')
        for source in sorted((root/module).glob('*')):
            if source.suffix.lower() not in {'.css','.js'}:continue
            if source.is_symlink():raise ValueError('Symlink runtime resource: '+str(source))
            target=out/module/source.name;target.parent.mkdir(parents=True,exist_ok=True)
            if source.suffix.lower()=='.css' and base:target.write_text(rewrite_css(source.read_text(),base))
            else:shutil.copyfile(source,target)
    copy_runtime(root/'toilet',out/'toilet')
    copy_runtime(root/'pi5/57store/system/static',out/'pi5/57store/system/static')
    copy_runtime(root/'pi5/57store/data',out/'pi5/57store/data')
    for board,values in public.items():
        for post in values:
            source=post['path'].parent/'assets'
            if source.exists():
                for asset in source.rglob('*'):
                    if not asset.is_file():continue
                    relative=asset.relative_to(post['path'].parent).as_posix();safe_asset(post['path'].parent,relative)
                    target=out/board/post['meta']['id']/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,target)
    def template(name):
        source=(root/name).read_text()
        if '{{terminal_header}}' in source:
            source=source.replace('{{terminal_header}}',(root/'templates/terminal-header.html').read_text())
        page=BeautifulSoup(source,'html.parser')
        if name in {'sys/page.html','cctv/page.html'}:
            board=Path(name).parent.name
            page.select_one(f'.store-module-select a[href="/{board}/"]')['aria-current']='page'
        return page
    def route(board,number):return '/'+board+'/' if number==1 else f'/{board}/page/{number}/'
    canonical_routes=[]
    def save(route_,kind,body,title,post=None,page_number=1):
        frame='{{content}}' if kind=='home' else (root/'templates/frame.html').read_text()
        if frame.count('{{content}}')!=1:raise ValueError('Frame needs one content slot')
        wrapped=BeautifulSoup(frame.replace('{{content}}',str(body)),'html.parser')
        if kind=='cache':
            column=wrapped.select_one('.entry-content').parent
            column['class']=column.get('class',[])+['cache-column']
        if kind in {'sys','cctv'}:
            column=wrapped.select_one('.entry-content').parent
            column['class']=column.get('class',[])+['store-terminal-column']
            frame=column.parent
            frame['class']=frame.get('class',[])+['store-terminal-frame']
        for el in wrapped.find_all():
            for attr in ('href','src','poster'):
                if el.get(attr):el[attr]=prefixed(el[attr],base)
            if el.get('srcset'):
                el['srcset']=', '.join(prefixed(p.strip().split()[0],base)+' '+p.strip().split()[-1] for p in el['srcset'].split(','))
            if el.get('style'):el['style']=rewrite_css(el['style'],base)
        styles=[]
        resources=['store/style.css'] if kind=='home' else ['site-assets/base.css','site-assets/terminal.css' if kind in {'sys','cctv'} else kind+'/style.css']
        if kind!='home':resources.append('site-assets/links.css')
        for resource in resources:
            path=root/resource;version='?v='+digest(path)[:12]
            styles.append(f'<link rel="stylesheet" href="{base}/{resource}{version}">')
        script=''
        if kind in {'home','cache'}:
            resource='store/visit.js' if kind=='home' else 'cache/reveal.js'
            source=root/resource;version='?v='+digest(source)[:12]
            script=f'<script src="{base}/{resource}{version}" defer></script>'
        html_class=' class="store-terminal-root"' if kind in {'sys','cctv'} else ''
        description=DESCRIPTIONS[kind]+(f' 第 {page_number} 页。' if page_number>1 else '')
        cover='site-assets/images/pages/57store/57store20260224f.webp'
        image=SITE_URL+'/'+cover if (root/cover).is_file() else None
        image_alt='五月七日便利店'
        if post:
            meta=post['meta']
            description=compact_text(meta.get('summary') or BeautifulSoup(render_body(post,kind),'html.parser').get_text(' ',strip=True),meta['title']+' · '+kind.upper()+' / 57store。')
            resource=meta['extra'].get('image','')
            if resource.startswith('assets/'):
                image=SITE_URL+quote('/'+kind+'/'+meta['id']+'/'+resource,safe='/')
                image_alt=meta['extra'].get('alt','') or meta['title']
        metadata=metadata_head(title,description,SITE_URL+quote(route_,safe='/'),site_name='五月七日便利店 · 57store',image=image,image_alt=image_alt,article=post is not None)
        body_class='store-home' if kind=='home' else 'wp-embed-responsive store-'+kind
        text=f'<!doctype html><html lang="zh-CN"{html_class}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#131415"><title>{html.escape(title)}</title>'+metadata+''.join(styles)+f'</head><body class="{body_class}">'+str(wrapped)+script+'</body></html>'
        target=out/route_.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        canonical_routes.append(route_)
    def paginate(page,board,number,total):
        nav=page.select_one('.wp-block-query-pagination')
        if nav is None:raise ValueError('Missing pagination template')
        nav.clear();nav['aria-label']=board.upper()+' pages'
        def link(n,label,cls,aria=None,rel=None):
            el=page.new_tag('a',attrs={'href':route(board,n),'class':cls})
            if aria:el['aria-label']=aria
            if rel:el['rel']=rel
            el.string=label;return el
        if number>1:nav.append(link(number-1,'«','wp-block-query-pagination-previous pager-arrow','上一页','prev'))
        for n in range(1,total+1):
            if n==number:
                el=page.new_tag('span',attrs={'class':'page-numbers current','aria-current':'page'});el.string=str(n)
            else:el=link(n,str(n),'page-numbers')
            nav.append(el)
        if number<total:nav.append(link(number+1,'»','wp-block-query-pagination-next pager-arrow','下一页','next'))
    def card(board,post,detail=False):
        page=template(f'{board}/card.html');item=page.li;ident=post['meta']['id'];item['id']=ident
        time=page.select_one('time');time['datetime']=post['meta']['extra']['published_at'];time.string=post['datetime'].strftime('%Y-%m-%d %H:%M')
        if not detail:
            anchor=page.new_tag('a',attrs={'href':f'/{board}/{ident}/','class':'store-entry-link','style':'color:inherit;text-decoration:none','aria-label':'Open '+board.upper()+' '+time.get_text()})
            time.wrap(anchor)
        entry=page.select_one('.entry-content');figure=deepcopy(entry.select_one('figure')) if board=='cctv' else None;entry.clear()
        if board=='cctv':
            for video_id in post['meta']['extra']['video_ids']:
                if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video_id):raise ValueError('Invalid video ID')
                embed=deepcopy(figure);iframe=embed.select_one('iframe');parsed=urlsplit(iframe['src'])
                iframe['src']=urlunsplit((parsed.scheme,parsed.netloc,'/embed/'+video_id,parsed.query,''));iframe['title']=post['meta']['title'];entry.append(embed)
        for el in list(BeautifulSoup(render_body(post,board),'html.parser').contents):entry.append(el)
        return item
    orders={};pages={}
    for board,values in public.items():
        total=max(1,(len(values)+SIZES[board]-1)//SIZES[board]);pages[board]=total
        orders[board]=[p['meta']['id'] for p in values]
        for n in range(1,total+1):
            page=template(f'{board}/page.html');listing=page.select_one('ul.wp-block-post-template');listing.clear()
            for post in values[(n-1)*SIZES[board]:n*SIZES[board]]:listing.append(card(board,post))
            paginate(page,board,n,total);save(route(board,n),board,page,'57store / '+board,page_number=n)
        for index,post in enumerate(values):
            page=template(f'{board}/page.html');listing=page.select_one('ul.wp-block-post-template');listing.clear();listing.append(card(board,post,True))
            page.select_one('.wp-block-query-pagination').decompose()
            back=page.new_tag('p',attrs={'class':'store-return','style':'font-size:10px'});a=page.new_tag('a',attrs={'href':route(board,index//SIZES[board]+1)+'#'+post['meta']['id']});a.string='◁ '+board;back.append(a)
            page.select_one('.wp-block-query').insert_before(back)
            save(f"/{board}/{post['meta']['id']}/",board,page,post['meta']['title']+' · 57store',post=post)
    pages['cache']=1
    page=template('cache/page.html');listing=page.select_one('ul.wp-block-post-template');listing.clear()
    for post in cache:
        item=template('cache/card.html').li;item['id']='cache-'+datetime.fromisoformat(post['published_at']).strftime('%Y%m%d-%H%M%S')
        time=item.select_one('time')
        if post.get('reveal'):
            time.parent.decompose();item['class']=item.get('class',[])+['store-reveal']
        else:
            time['datetime']=post['published_at'];time.string=post['published_at']
        entry=item.select_one('.entry-content');entry.clear()
        if post.get('reveal'):
            target_id=item['id']+'-content';input_id=item['id']+'-input'
            fragment=BeautifulSoup(f'<form class="cache-access" method="dialog" data-cache-reveal="{target_id}"><label class="cache-access-label" for="{input_id}">password / 口令</label><div class="cache-access-controls"><input class="cache-access-input" id="{input_id}" type="password" name="cache_code" placeholder="••••••" spellcheck="false" autocomplete="off"><button class="cache-access-send" type="submit">发送 <span aria-hidden="true">↵</span></button></div></form><div id="{target_id}" data-cache-reveal-content aria-live="polite" hidden></div>','html.parser')
            target=fragment.select_one('[data-cache-reveal-content]')
            for el in list(BeautifulSoup(post['body_html'],'html.parser').contents):target.append(el)
            for el in list(fragment.contents):entry.append(el)
        else:
            for el in list(BeautifulSoup(post['body_html'],'html.parser').contents):entry.append(el)
        listing.append(item)
    save('/cache/','cache',page,'57store / .cache')
    # Old conversation bookmarks return to the continuous thread.
    legacy=out/'cache/page/2/index.html';legacy.parent.mkdir(parents=True,exist_ok=True)
    destination=base+'/cache/#'+('cache-'+datetime.fromisoformat(cache[-1]['published_at']).strftime('%Y%m%d-%H%M%S') if cache else '')
    legacy_metadata=metadata_head('.cache',DESCRIPTIONS['cache'],SITE_URL+'/cache/',site_name='五月七日便利店 · 57store')
    legacy.write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+html.escape(destination,quote=True)+'">'+legacy_metadata+'<title>.cache</title></head><body><a href="'+html.escape(destination,quote=True)+'">.cache</a></body></html>')
    receipt=template('receipt/page.html')
    for key,unit in [('revisions','entries'),('receipts','receipts')]:
        slots=receipt.select(f'[data-store-stat="{key}"]')
        if len(slots)!=1:raise ValueError('Receipt needs one statistic slot: '+key)
        slots[0].string=f'{stats[key]:,} {unit}'
    save('/receipt/','receipt',receipt,'57store / receipt')
    save('/','home',home,'五月七日便利店 · 57store')
    save('/fragment/','fragment',template('fragment/page.html'),'57store / fragment')
    # Retained experiments keep their original body and scripts; enrich only their head.
    for retained in sorted(out.rglob('*.html')):
        relative=retained.relative_to(out).as_posix()
        route_='/'+relative.removesuffix('index.html') if retained.name=='index.html' else '/'+relative
        if route_ in canonical_routes or retained==legacy:continue
        document=retained.read_text()
        head=BeautifulSoup(document,'html.parser').head
        if head is None:continue
        title=head.title.get_text() if head.title else '57store'
        description='Toilet · 五月七日便利店的独立空间。' if route_.startswith('/toilet/') else '57store · 店内系统的静态记录。'
        metadata=metadata_head(title,description,SITE_URL+quote(route_,safe='/'),site_name='五月七日便利店 · 57store')
        retained.write_text(add_missing_metadata(document,metadata))
        canonical_routes.append(route_)
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(SITE_URL+quote(route_,safe='/'))+'</loc></url>' for route_ in sorted(set(canonical_routes)))+'</urlset>')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE_URL+'/sitemap.xml\n')
    (out/'.nojekyll').write_text('')
    if (root/'CNAME').exists():shutil.copyfile(root/'CNAME',out/'CNAME')
    files={p.relative_to(out).as_posix():digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
    receipt={'version':1,'files':files,'fingerprint':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),'counts':{**{b:len(v) for b,v in public.items()},'cache':len(cache)},'store_stats':stats,'pages':pages,'order':orders,'base_path':base}
    (out/'build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'counts':receipt['counts'],'pages':pages,'files':len(files),'output':str(out)}));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path);parser.add_argument('--base-path',default='')
    args=parser.parse_args();build(args.root,args.output,args.base_path)
