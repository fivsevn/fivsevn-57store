"""Exercise publication boundaries, pagination, path prefixes and content integrity."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import build,load_posts
from check import check
from site_post_metadata import normalize_metadata,dump_frontmatter


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup);self.root=Path(self.temporary.name)
        for folder in ['templates','schemas','site-assets']:
            shutil.copytree(ROOT/folder,self.root/folder)
        (self.root/'cache').mkdir();shutil.copyfile(ROOT/'cache/page.html',self.root/'cache/page.html')
        (self.root/'fragment').mkdir();shutil.copyfile(ROOT/'fragment/page.html',self.root/'fragment/page.html')
        (self.root/'site-data').mkdir();(self.root/'site-data/content.json').write_text(json.dumps({'retained_posts':{},'assets':[]}))
        (self.root/'cache/posts.json').write_text(json.dumps([{'title':'cache','published_at':f'2026-06-08T18:{n:02d}:00+08:00','body_html':f'<p>message {n}</p>'} for n in range(11)]))
        (self.root/'toilet/assets').mkdir(parents=True);(self.root/'toilet/index.html').write_text('<img src="assets/original.png">');(self.root/'toilet/assets/original.png').write_bytes(b'preserved image')
        pi=self.root/'pi5/57store/system';(pi/'static').mkdir(parents=True);(pi/'static/index.html').write_text('<link rel="stylesheet" href="/static/style.css"><script src="/static/app.js"></script>');(pi/'static/style.css').write_text('body { color:white; }');(pi/'static/app.js').write_text('const snapshot = true;');(pi/'app.py').write_text('PRIVATE_BACKEND_SOURCE')
        (self.root/'pi5/57store/data').mkdir();(self.root/'pi5/57store/data/weather.json').write_text('{"snapshot":true}')
        for n in range(16):self.post('sys',f'sys-{n}',f'2026-06-08T18:{n:02d}:00+08:00',body=f'system message {n}\n')
        self.post('cctv','first','2026-06-08T19:00:00+08:00',body='**authored note**\n',video='AbCdEfG0001')
        self.post('cctv','second','2026-06-08T20:00:00+08:00',video='AbCdEfG0002')

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
        self.assertFalse((self.root/'_site/sys/hidden').exists());self.assertFalse((self.root/'_site/sys/private').exists())
        self.assertFalse(any(p.name=='secret.png' for p in (self.root/'_site').rglob('*')))

    def test_project_base_path_covers_navigation_css_and_existing_static_frontend(self):
        build(self.root,base_path='/preview');check(self.root,base_path='/preview')
        page=BeautifulSoup((self.root/'_site/sys/page/2/index.html').read_text(),'html.parser')
        self.assertEqual(page.select_one('.wp-block-query-pagination-previous')['href'],'/preview/sys/')
        self.assertTrue(all(link['href'].startswith('/preview/') for link in page.select('link[rel=stylesheet]')))
        self.assertIn('/preview/pi5/57store/system/static/style.css',(self.root/'_site/pi5/57store/system/static/index.html').read_text())

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
        self.assertTrue(page.select_one('script[src*="/site-assets/cache.js"]'))
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


if __name__=='__main__':unittest.main()
