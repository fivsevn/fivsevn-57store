"""Exercise publication boundaries, pagination, path prefixes and content integrity."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import build,load_posts,store_revisions
from check import check
from site_post_metadata import normalize_metadata,dump_frontmatter


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup);self.root=Path(self.temporary.name)
        for folder in ['templates','schemas','site-assets','store','receipt','cache','fragment']:
            shutil.copytree(ROOT/folder,self.root/folder)
        for board in ('sys','cctv'):
            (self.root/board).mkdir()
            for name in ('page.html','card.html'):
                shutil.copyfile(ROOT/board/name,self.root/board/name)
        (self.root/'site-data').mkdir();(self.root/'site-data/content.json').write_text(json.dumps({'retained_posts':{},'assets':[]}))
        (self.root/'cache/posts.json').write_text(json.dumps([{'title':'cache','published_at':f'2026-06-08T18:{n:02d}:00+08:00','body_html':f'<p>message {n}</p>'} for n in range(11)]))
        (self.root/'toilet/assets').mkdir(parents=True);(self.root/'toilet/index.html').write_text('<img src="assets/original.png">');(self.root/'toilet/assets/original.png').write_bytes(b'preserved image')
        pi=self.root/'pi5/57store/system';(pi/'static').mkdir(parents=True);(pi/'static/index.html').write_text('<link rel="stylesheet" href="/static/style.css"><script src="/static/app.js"></script>');(pi/'static/style.css').write_text('body { color:white; }');(pi/'static/app.js').write_text('const snapshot = true;');(pi/'app.py').write_text('PRIVATE_BACKEND_SOURCE')
        (self.root/'pi5/57store/data').mkdir();(self.root/'pi5/57store/data/weather.json').write_text('{"snapshot":true}')
        for n in range(16):self.post('sys',f'sys-{n}',f'2026-06-08T18:{n:02d}:00+08:00',body=f'system message {n}\n')
        self.post('cctv','first','2026-06-08T19:00:00+08:00',body='**authored note**\n',video='AbCdEfG0001')
        self.post('cctv','second','2026-06-08T20:00:00+08:00',video='AbCdEfG0002')
        self.git('init','-q')
        self.git('add','.')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Initial store')

    def git(self,*args):
        return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True,text=True).stdout.strip()

    def post(self,board,ident,date,body='',video=None,status='published',visibility='public'):
        extra={'published_at':date}
        if video:extra['video_ids']=[video]
        meta=normalize_metadata({'id':ident,'title':ident,'status':status,'visibility':visibility,'extra':extra},site=board)
        path=self.root/board/'2026/06'/ident/'index.md';path.parent.mkdir(parents=True);path.write_text(dump_frontmatter(meta)+body);return path

    def test_lists_details_notes_pagination_and_preserved_experiments(self):
        receipt=build(self.root);result=check(self.root)
        self.assertEqual(receipt['pages'],{'sys':2,'cctv':1,'cache':1})
        self.assertEqual(receipt['order']['sys'],[f'sys-{n}' for n in reversed(range(16))])
        detail=BeautifulSoup((self.root/'_site/sys/sys-0/index.html').read_text(),'html.parser')
        self.assertEqual(detail.select_one('.store-return a')['href'],'/sys/page/2/#sys-0')
        video=BeautifulSoup((self.root/'_site/cctv/index.html').read_text(),'html.parser')
        self.assertEqual([x['id'] for x in video.select('li.wp-block-post')],['second','first'])
        self.assertIn('authored note',video.get_text())
        cache=BeautifulSoup((self.root/'_site/cache/index.html').read_text(),'html.parser')
        self.assertIn('message 10',cache.get_text());self.assertIn('message 0',cache.get_text())
        self.assertEqual(len(cache.select('ul.wp-block-post-template > li')),11)
        self.assertFalse(cache.select('.wp-block-query-pagination'))
        old=BeautifulSoup((self.root/'_site/cache/page/2/index.html').read_text(),'html.parser')
        self.assertEqual(old.select_one('meta[http-equiv=refresh]')['content'],'0;url=/cache/#cache-20260608-181000')
        self.assertEqual((self.root/'_site/toilet/assets/original.png').read_bytes(),b'preserved image')
        self.assertFalse((self.root/'_site/pi5/57store/system/app.py').exists())
        self.assertIn('/pi5/57store/system/static/app.js',(self.root/'_site/pi5/57store/system/static/index.html').read_text())
        self.assertEqual(result['broken_links'],0)

    def test_hidden_status_and_private_visibility_exclude_packages_and_images(self):
        for ident,status,visibility in [('hidden','hidden','public'),('private','published','private')]:
            source=self.post('sys',ident,'2026-06-08T22:00:00+08:00',body='![private](assets/secret.png)',status=status,visibility=visibility)
            (source.parent/'assets').mkdir();(source.parent/'assets/secret.png').write_bytes(b'PRIVATE_IMAGE')
        receipt=build(self.root);check(self.root)
        self.assertEqual(receipt['counts']['sys'],16)
        self.assertEqual(receipt['store_stats']['receipts'],18)
        self.assertFalse((self.root/'_site/sys/hidden').exists());self.assertFalse((self.root/'_site/sys/private').exists())
        self.assertFalse(any(p.name=='secret.png' for p in (self.root/'_site').rglob('*')))

    def test_project_base_path_covers_navigation_css_and_existing_static_frontend(self):
        build(self.root,base_path='/preview');check(self.root,base_path='/preview')
        page=BeautifulSoup((self.root/'_site/sys/page/2/index.html').read_text(),'html.parser')
        self.assertEqual(page.select_one('.wp-block-query-pagination-previous')['href'],'/preview/sys/')
        self.assertTrue(all(link['href'].startswith('/preview/') for link in page.select('link[rel=stylesheet]')))
        self.assertIn('/preview/pi5/57store/system/static/style.css',(self.root/'_site/pi5/57store/system/static/index.html').read_text())

    def test_terminal_header_preserves_module_selection_inside_each_frame(self):
        build(self.root,base_path='/preview')
        for board,ident,selected in [('sys','sys-0','1'),('cctv','first','2')]:
            for route in [board,board+'/'+ident]:
                with self.subTest(route=route):
                    page=BeautifulSoup((self.root/'_site'/route/'index.html').read_text(),'html.parser')
                    frame=page.select_one('.store-terminal-frame')
                    headers=frame.select('.store-terminal-header')
                    self.assertEqual(len(headers),1)
                    header=headers[0]
                    self.assertIn('BOOT SEQUENCE INIT',header.get_text())
                    self.assertIn('SYSTEM ONLINE',header.get_text())
                    rows=header.select('.store-module-row')
                    self.assertEqual([row['href'] for row in rows],['/preview/sys/','/preview/cctv/'])
                    self.assertEqual([row.get_text(' ',strip=True) for row in rows],[
                        '(1) TERMINAL.LOG … operator log / expiry',
                        '(2) CCTV.MONITOR … camera index / event stream',
                    ])
                    selection=header.select_one('.store-module-select')
                    self.assertEqual([a.get_text(strip=True) for a in selection.select('a')],['1','2'])
                    self.assertEqual([a['href'] for a in selection.select('a')],['/preview/sys/','/preview/cctv/'])
                    self.assertEqual([a.get_text(strip=True) for a in selection.select('a[aria-current="page"]')],[selected])
                    self.assertEqual(selection.get_text(' ',strip=True),'SELECT: [ 1 ] [ 2 ]')
                    self.assertNotIn('{{terminal_header}}',str(page))
                    if '/' in route:
                        self.assertFalse(frame.select('.wp-block-query-pagination'))
                    else:
                        self.assertIsNotNone(frame.select_one('.wp-block-query-pagination'))
        single=BeautifulSoup((self.root/'_site/cctv/index.html').read_text(),'html.parser')
        pager=single.select_one('.wp-block-query-pagination')
        self.assertEqual(pager.get_text(' ',strip=True),'1')
        self.assertEqual(pager.select_one('[aria-current="page"]').name,'span')
        self.assertFalse(pager.select('a'))

    def test_terminal_pagination_has_flat_numbers_and_adjacent_arrows_on_every_page(self):
        for n in range(16,31):
            self.post('sys',f'sys-{n}',f'2026-06-08T18:{n:02d}:00+08:00',body=f'system message {n}\n')
        for n in range(2,35):
            self.post('cctv',f'camera-{n}',f'2026-06-08T21:{n:02d}:00+08:00',video=f'CamTest{n:04d}')
        receipt=build(self.root,base_path='/preview')
        self.assertEqual(receipt['pages'],{'sys':3,'cctv':3,'cache':1})
        for board in ['sys','cctv']:
            def route(number):
                return f'/preview/{board}/' if number==1 else f'/preview/{board}/page/{number}/'
            for number in [1,2,3]:
                with self.subTest(board=board,page=number):
                    path=self.root/'_site'/board
                    if number>1:path=path/'page'/str(number)
                    page=BeautifulSoup((path/'index.html').read_text(),'html.parser')
                    frame=page.select_one('.store-terminal-frame')
                    pager=frame.select_one('.wp-block-query-pagination')
                    self.assertIsNotNone(pager)
                    self.assertIsNotNone(pager.parent.select_one('ul.wp-block-post-template'))
                    self.assertEqual([el.get_text(strip=True) for el in pager.select('.page-numbers')],['1','2','3'])
                    self.assertTrue(all(el.name in ['a','span'] for el in pager.find_all(recursive=False)))
                    current=pager.select('[aria-current="page"]')
                    self.assertEqual(len(current),1)
                    self.assertEqual(current[0].name,'span')
                    self.assertEqual(current[0].get_text(),str(number))
                    for link in pager.select('a.page-numbers'):
                        self.assertEqual(link['href'],route(int(link.get_text())))
                    for direction,target,glyph,relation,visible in [
                        ('previous',number-1,'«','prev',number>1),
                        ('next',number+1,'»','next',number<3),
                    ]:
                        arrow=pager.select_one('.wp-block-query-pagination-'+direction)
                        if visible:
                            self.assertIsNotNone(arrow)
                            self.assertIn('pager-arrow',arrow.get('class',[]))
                            self.assertEqual(arrow.get_text(),glyph)
                            self.assertEqual(arrow['href'],route(target))
                            self.assertIn(relation,arrow.get('rel',[]))
                            self.assertTrue(arrow.get('aria-label'))
                        else:self.assertIsNone(arrow)

    def test_duplicate_video_is_rejected_even_when_other_record_hidden(self):
        self.post('cctv','duplicate','2026-06-08T23:00:00+08:00',video='AbCdEfG0001',status='hidden')
        with self.assertRaisesRegex(ValueError,'Duplicate CCTV video ID'):build(self.root)

    def test_cache_reveal_accepts_empty_input_and_contains_only_the_authored_public_reply(self):
        path=self.root/'cache/posts.json';data=json.loads(path.read_text());data[-1].update(reveal=True,body_html='<p><a href="https://fivsevn.com/">fivsevn.com</a></p>');path.write_text(json.dumps(data))
        receipt=build(self.root);check(self.root)
        page=BeautifulSoup((self.root/'_site/cache/index.html').read_text(),'html.parser')
        item=page.select_one('li.store-reveal');form=item.select_one('form[data-cache-reveal]');reply=item.select_one('[data-cache-reveal-content]')
        self.assertIsNotNone(form)
        self.assertEqual(item['id'],'cache-20260608-181000')
        self.assertFalse(form.has_attr('action'));self.assertFalse(form.select_one('input[type=password]').has_attr('required'))
        self.assertEqual(form['method'],'dialog')
        self.assertTrue(reply.has_attr('hidden'));self.assertEqual(reply.a['href'],'https://fivsevn.com/')
        self.assertFalse(item.select('time'))
        self.assertTrue(page.select_one('script[src*="/cache/reveal.js"]'))
        self.assertEqual(receipt['counts']['cache'],11)

    def test_new_sys_plain_two_line_entry_keeps_its_line_break(self):
        self.post('sys','two-lines','2026-06-08T23:00:00+08:00',body='English line\n中文行\n')
        build(self.root);page=BeautifulSoup((self.root/'_site/sys/two-lines/index.html').read_text(),'html.parser');body=page.select_one('li#two-lines .entry-content')
        self.assertEqual(len(body.select('br')),1)
        self.assertEqual(body.get_text(' ',strip=True),'English line 中文行')

    def test_unsafe_image_fails_before_it_can_copy_a_source_file(self):
        self.post('sys','unsafe','2026-06-08T23:00:00+08:00',body='![bad](assets/../../private.png)')
        (self.root/'private.png').write_bytes(b'PRIVATE')
        with self.assertRaisesRegex(ValueError,'inside assets'):build(self.root)
        self.assertFalse(any(p.name=='private.png' for p in (self.root/'_site').rglob('*')))

    def test_changed_authored_content_is_detected_even_with_rehashed_receipt(self):
        build(self.root);site=self.root/'_site';detail=site/'sys/sys-0/index.html';detail.write_text(detail.read_text().replace('system message 0','different content'))
        receipt=json.loads((site/'build-receipt.json').read_text());receipt['files']['sys/sys-0/index.html']=hashlib.sha256(detail.read_bytes()).hexdigest();receipt['fingerprint']=hashlib.sha256(json.dumps(receipt['files'],sort_keys=True).encode()).hexdigest();(site/'build-receipt.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'Changed authored body'):check(self.root)

    def test_source_directory_cannot_be_used_as_output(self):
        with self.assertRaisesRegex(ValueError,'source directory'):build(self.root,output=self.root/'toilet')
        self.assertTrue((self.root/'toilet/index.html').exists())

    def test_store_statistics_follow_commits_and_public_entries_without_changing_on_rebuild(self):
        first=build(self.root)
        self.assertEqual(first['store_stats'],{'revisions':1,'receipts':18})
        self.assertEqual(build(self.root)['fingerprint'],first['fingerprint'])
        self.post('sys','new-receipt','2026-06-08T23:00:00+08:00',body='new receipt')
        self.git('add','sys')
        self.git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Publish receipt')
        with self.assertRaisesRegex(ValueError,'Store statistics differ'):check(self.root)
        final=build(self.root);check(self.root)
        self.assertEqual(final['store_stats'],{'revisions':2,'receipts':19})
        home=BeautifulSoup((self.root/'_site/receipt/index.html').read_text(),'html.parser')
        self.assertEqual(home.select_one('[data-store-stat=revisions]').get_text(),'2 entries')
        self.assertEqual(home.select_one('[data-store-stat=receipts]').get_text(),'19 receipts')

    def test_store_routes_module_boundaries_and_authored_labels(self):
        build(self.root,base_path='/preview');check(self.root,base_path='/preview')
        site=self.root/'_site'
        page=BeautifulSoup((site/'index.html').read_text(),'html.parser')
        config=json.loads((self.root/'store/config.json').read_text())
        self.assertEqual(sorted(a['href'] for a in page.select('a[href]')),['/preview/cctv/','/preview/receipt/','/preview/sys/'])
        art=page.select_one('svg.store-art')
        self.assertIsNotNone(art)
        self.assertFalse(art.select('image,foreignObject,foreignobject,script,iframe'))
        colours={element['fill'].lower() for element in art.select('[fill]') if element['fill'].startswith('#')}
        self.assertLessEqual(len(colours),8,'57store uses a restrained charcoal/mint palette')
        self.assertIn('#131415',colours)
        self.assertIn('#53efc0',colours)
        for element in art.find_all(True):
            for attribute in ('href','xlink:href','src'):
                if element.has_attr(attribute):
                    self.assertTrue(element[attribute].startswith('#'),'Scene must be drawn in code without external assets')
        self.assertFalse(page.select('header,footer,.wp-site-blocks'))
        self.assertTrue(page.select_one('script[src^="/preview/store/interactions.js"]'))
        self.assertEqual(len(page.select('button.store-object')),len(config['fixtures']))
        for entry in config['entries']:
            if entry['id'] in ('sys','cctv'):
                coldstock=next(f['bounds'] for f in config['fixtures'] if f['id']=='coldstock')
                self.assertGreaterEqual(entry['bounds'][1],coldstock[1]+coldstock[3],'Internal computers are behind the cold-room stock area')
        for fixture in ('toiletdoor','toilet','toiletbasin','staffwork','stock','receiving','staffbreak','lockers','cleaning'):
            self.assertIsNotNone(page.select_one(f'#fixture-{fixture}'))
            self.assertIsNotNone(page.select_one(f'button[data-store-object="{fixture}"]'))
        self.assertFalse(page.select('a[href*="toilet"],a[href*="cache"],a[href*="fragment"]'))
        for button in page.select('button.store-object'):
            label=page.find(id=button['aria-controls'])
            self.assertIsNotNone(label)
            self.assertTrue(label.has_attr('hidden'))
            self.assertEqual(label['role'],'status')
            self.assertTrue(label.select_one('strong'))
        self.assertFalse(page.select('dialog'))
        self.assertNotIn('STAFF ONLY',page.get_text())
        self.assertIn('每日生活、本地缓存。',page.get_text())
        receipt=BeautifulSoup((site/'receipt/index.html').read_text(),'html.parser')
        self.assertIn('TIME IS NON-REFUNDABLE',receipt.get_text())
        returns=receipt.select('.receipt-return')
        self.assertEqual(len(returns),1)
        self.assertEqual(returns[0].a['href'],'/preview/')
        comment=returns[0].parent
        self.assertEqual(comment.find_previous_sibling('p').get_text(strip=True),'// store.rs')
        lines=comment.find_all('p',recursive=False)
        self.assertEqual(lines[0].get_text(strip=True),'/*')
        self.assertEqual(lines[-1].get_text(strip=True),'*/')
        printer=next(p for p in lines if p.get_text().startswith('receipt printer:'))
        self.assertLess(lines.index(returns[0]),lines.index(printer))
        ticket=receipt.select_one('.has-border-color.has-base-background-color')
        self.assertIn('GOOD NIGHT.',ticket.get_text())
        self.assertFalse(ticket.select('.receipt-return,a[href="/preview/"]'))
        self.assertFalse((self.root/'templates/home.html').exists())
        for source in ('page.html','scene.py','equipment.py','furnishings.py','config.json'):
            self.assertFalse((site/'store'/source).exists())
        self.assertFalse((site/'receipt/page.html').exists())
        for board in ('sys','cctv'):
            terminal=BeautifulSoup((site/board/'index.html').read_text(),'html.parser')
            self.assertFalse(terminal.select('.store-terminal-header a[href="/preview/receipt/"]'))
            self.assertEqual(terminal.select_one('.store-session-exit a')['href'],'/preview/')
        for directory in ('store','receipt'):
            with self.assertRaisesRegex(ValueError,'source directory'):
                build(self.root,output=self.root/directory)

    def test_store_statistics_reject_incomplete_git_history(self):
        clone=self.root/'shallow'
        subprocess.run(['git','clone','--quiet','--depth','1',self.root.as_uri(),str(clone)],check=True,capture_output=True)
        with self.assertRaisesRegex(ValueError,'complete history'):store_revisions(clone)


if __name__=='__main__':unittest.main()
