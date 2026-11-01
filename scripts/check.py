#!/usr/bin/env python3
"""Validate the generated public site, retained content and publication boundaries."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
from bs4 import BeautifulSoup
from build import ROOT, SIZES, base_prefix, digest, is_published, load_posts, render_body


def check(root=ROOT, output=None, base_path=''):
    root=Path(root).resolve();out=Path(output) if output else root/'_site'
    if not out.is_absolute():out=root/out
    base=base_prefix(base_path);errors=[]
    receipt=json.loads((out/'build-receipt.json').read_text())
    files={p.relative_to(out).as_posix():digest(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='build-receipt.json'}
    if files!=receipt.get('files'):errors.append('Public files differ from the build receipt')
    if hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()!=receipt.get('fingerprint'):errors.append('Build receipt fingerprint is invalid')
    if receipt.get('base_path')!=base:errors.append('Build receipt base path differs')
    manifest=json.loads((root/'site-data/content.json').read_text());posts=load_posts(root)
    for board,retained in manifest.get('retained_posts',{}).items():
        present={p['meta']['id'] for p in posts[board]}
        if not set(retained)<=present:errors.append('Retained archive records are missing: '+board)
    for item in manifest.get('assets',[]):
        source=root/item['path'];target=out/item['path']
        if not source.is_file() or source.stat().st_size!=item['bytes'] or digest(source)!=item['sha256']:errors.append('Shared asset source changed: '+item['path'])
        if not target.is_file() or digest(target)!=item['sha256']:errors.append('Shared asset output changed: '+item['path'])
    def target_for(relative,value):
        if not value:return None
        parsed=urlsplit(value)
        if parsed.scheme or parsed.netloc:return None
        if not parsed.path:return None
        target=urlsplit(urljoin('https://local.invalid'+base+'/'+relative,value)).path
        if base:
            if not (target==base or target.startswith(base+'/')):
                errors.append('Unprefixed local URL: '+relative+': '+value);return None
            target=target[len(base):] or '/'
        dest=(out/unquote(target).lstrip('/')).resolve()
        if not dest.is_relative_to(out.resolve()):errors.append('URL leaves output: '+value);return None
        if dest.is_dir():dest=dest/'index.html'
        if not dest.is_file():errors.append('Broken local URL: '+relative+': '+value)
        return dest
    for relative in files:
        path=out/relative
        if path.suffix.lower() in {'.md','.py','.yml','.yaml'} or any(part.startswith('.') and part!='.nojekyll' for part in Path(relative).parts):errors.append('Source or private file published: '+relative)
        if path.suffix.lower() not in {'.html','.css','.js'}:continue
        text=path.read_text()
        if re.search(r'footer\.rs|rest_route=|http_envelope=|(?:[?&]|&#038;)token=',text):errors.append('Retired footer or signed API token: '+relative)
        if path.suffix.lower()=='.html':
            soup=BeautifulSoup(text,'html.parser')
            for el in soup.find_all():
                for attr in ('href','src','poster'):
                    value=el.get(attr)
                    if not value:continue
                    parsed=urlsplit(value)
                    if attr in {'src','poster'} and parsed.scheme in {'https','http'}:
                        allowed=el.name=='iframe' and parsed.hostname in {'www.youtube.com','youtube.com','www.youtube-nocookie.com'}
                        if not allowed:errors.append('External runtime asset: '+relative+': '+value)
                    if el.name=='link' and 'stylesheet' in el.get('rel',[]) and parsed.netloc:errors.append('External stylesheet: '+relative)
                    target_for(relative,value)
                if el.get('srcset'):
                    for part in el['srcset'].split(','):
                        target_for(relative,part.strip().split()[0])
                if el.get('style'):
                    for match in re.finditer(r'url\(\s*[\'"]?([^\)\'\"]+)',el['style']):target_for(relative,match[1])
        else:
            for match in re.finditer(r'url\(\s*[\'"]?([^\)\'\"]+)',text):
                value=match[1].strip()
                if urlsplit(value).scheme in {'https','http'}:errors.append('External CSS resource: '+relative+': '+value[:100])
                target_for(relative,value)
    for board,values in posts.items():
        public=[p for p in values if is_published(p['meta'])]
        expected=[p['meta']['id'] for p in public];actual=[]
        count=max(1,(len(public)+SIZES[board]-1)//SIZES[board])
        for number in range(1,count+1):
            rel=board+'/index.html' if number==1 else f'{board}/page/{number}/index.html'
            page=BeautifulSoup((out/rel).read_text(),'html.parser')
            actual.extend(item.get('id') for item in page.select('ul.wp-block-post-template > li'))
        if actual!=expected:errors.append('Wrong public archive order: '+board)
        if receipt.get('counts',{}).get(board)!=len(public):errors.append('Wrong public post count: '+board)
        if receipt.get('order',{}).get(board)!=expected:errors.append('Receipt source order differs: '+board)
        for post in values:
            ident=post['meta']['id'];directory=out/board/ident
            if not is_published(post['meta']):
                if directory.exists():errors.append('Hidden package leaked: '+board+'/'+ident)
                continue
            detail=directory/'index.html'
            if not detail.exists():errors.append('Missing detail page: '+ident);continue
            page=BeautifulSoup(detail.read_text(),'html.parser');item=page.find('li',id=ident)
            if not item:errors.append('Detail identifies the wrong post: '+ident);continue
            stamp=item.select_one('time')
            if not stamp or stamp.get('datetime')!=post['meta']['extra']['published_at']:errors.append('Wrong precise publication time: '+ident)
            expected_text=BeautifulSoup(render_body(post,board),'html.parser').get_text(' ',strip=True)
            actual_text=item.select_one('.entry-content').get_text(' ',strip=True)
            if expected_text!=actual_text:errors.append('Changed authored body: '+ident)
            if board=='cctv':
                video_ids=[urlsplit(frame['src']).path.rsplit('/',1)[-1] for frame in item.select('iframe[src]')]
                if video_ids!=post['meta']['extra']['video_ids']:errors.append('Wrong video identity: '+ident)
    cache=json.loads((root/'cache/posts.json').read_text());cache.sort(key=lambda p:p['published_at']);messages=[]
    page=BeautifulSoup((out/'cache/index.html').read_text(),'html.parser')
    if page.select('.wp-block-query-pagination'):errors.append('Cache must be one continuous conversation')
    for item in page.select('ul.wp-block-post-template > li'):
        time=item.select_one('time')
        entry=item.select_one('.entry-content');revealed=entry.select_one('[data-cache-reveal-content]')
        messages.append((time.get('datetime') if time else None,(revealed or entry).get_text(' ',strip=True)))
        if revealed:
            form=entry.select_one('form[data-cache-reveal]')
            if not form or form.has_attr('action') or form.select_one('input[type=password]').has_attr('required'):
                errors.append('Cache reveal must accept any input without a network endpoint')
            if not revealed.has_attr('hidden'):errors.append('Cache reply must begin concealed')
    expected=[]
    for post in cache:
        expected.append((None if post.get('reveal') else post['published_at'],BeautifulSoup(post['body_html'],'html.parser').get_text(' ',strip=True)))
    if messages!=expected:errors.append('Cache conversation content/order changed')
    for source in [root/'toilet',root/'pi5/57store/system/static',root/'pi5/57store/data']:
        for file in source.rglob('*') if source.exists() else []:
            if file.is_file() and file.suffix.lower() not in {'.md','.py'} and not any(x.startswith('.') for x in file.relative_to(source).parts):
                target=out/file.relative_to(root)
                if not target.is_file():errors.append('Missing preserved experiment resource: '+str(file.relative_to(root)))
    if errors:raise ValueError('\n'.join(errors))
    result={'posts':{b:len([p for p in v if is_published(p['meta'])]) for b,v in posts.items()},'cache':len(cache),'files':len(files),'broken_links':0}
    print(json.dumps(result));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--output',type=Path);parser.add_argument('--base-path',default='')
    args=parser.parse_args();check(args.root,args.output,args.base_path)
