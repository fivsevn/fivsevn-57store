"""Verify the new store entrance and relocated receipt without live services."""
from pathlib import Path
import sys
import unittest
from urllib.parse import urlsplit
from xml.etree import ElementTree

from bs4 import BeautifulSoup

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build import build, render_store, SITE_URL
from check import check
import test_build as fixtures


class SiteModuleTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.BuildTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.root

    def page(self,route):
        return BeautifulSoup((self.root/'_site'/route/'index.html').read_text(),'html.parser')

    def test_entrance_is_standalone_and_receipt_keeps_the_old_content(self):
        build(self.root,base_path='/preview');check(self.root,base_path='/preview')
        entrance=self.page('');ticket=self.page('receipt')
        self.assertEqual(entrance.title.get_text(),'五月七日便利店 · 57store')
        self.assertEqual(entrance.select_one('link[rel=canonical]')['href'],SITE_URL+'/')
        self.assertEqual(ticket.select_one('link[rel=canonical]')['href'],SITE_URL+'/receipt/')
        self.assertFalse(entrance.select('.wp-site-blocks, .store-terminal-header'))
        self.assertEqual([urlsplit(a['href']).path for a in entrance.select('a[href]')],
                         ['/preview/receipt/','/preview/sys/','/preview/cctv/'])
        self.assertTrue(entrance.select_one('svg[role=img][aria-label]'))
        self.assertFalse(entrance.select('[data-store-stat]'))
        self.assertTrue(ticket.select_one('.wp-site-blocks'))
        self.assertIn('receipt printer: warming up…',ticket.get_text())
        self.assertEqual(len(ticket.select('[data-store-stat]')),2)
        returning=ticket.select_one('a.receipt-store-return')
        self.assertEqual(returning['href'],'/preview/')
        self.assertTrue(returning.parent.get_text().startswith('// store.rs'))
        self.assertLess(str(ticket).index('receipt-store-return'),str(ticket).index('receipt printer:'))
        self.assertFalse(returning.find_parent(class_='has-border-color'))
        sitemap=ElementTree.parse(self.root/'_site/sitemap.xml')
        self.assertIn(SITE_URL+'/receipt/',[node.text for node in sitemap.findall('{*}url/{*}loc')])

    def test_module_resources_ship_without_source_templates_or_renderers(self):
        build(self.root)
        site=self.root/'_site'
        self.assertTrue((site/'receipt/style.css').is_file())
        self.assertTrue((site/'cache/reveal.js').is_file())
        self.assertTrue((site/'fragment/assets/avatar202603fragment169.webp').is_file())
        self.assertTrue((site/'cache/assets/avatar202511nvesvif512.png').is_file())
        self.assertTrue((site/'receipt/assets/icons/facebook.png').is_file())
        for retired in ('site-assets/home.css','site-assets/cache.css','site-assets/cache.js','site-assets/fragment.css'):
            self.assertFalse((site/retired).exists(),retired)
        self.assertFalse((self.root/'templates/home.html').exists())
        self.assertEqual({p.name for p in (self.root/'templates').iterdir()},{'frame.html','terminal-header.html'})
        self.assertFalse(list(site.rglob('*.py')))
        self.assertFalse((site/'store/page.html').exists())
        self.assertFalse((site/'sys/card.html').exists())
        self.assertFalse((site/'receipt/page.html').exists())

    def test_terminals_offer_only_english_session_exit_in_the_existing_header(self):
        build(self.root,base_path='/preview')
        for route in ('sys','sys/page/2','sys/sys-0','cctv','cctv/first'):
            with self.subTest(route=route):
                header=self.page(route).select_one('.store-terminal-header')
                session=header.select_one('.store-session')
                self.assertEqual(session.get_text(' ',strip=True),'SESSION: [ EXIT ]')
                self.assertEqual(session.a['href'],'/preview/')
                self.assertEqual([a.get('href') for a in header.select('a[href*="receipt"]')],[])
                self.assertEqual(len(header.select('a[href="/preview/"]')),1)

    def test_bad_scene_contract_fails_before_replacing_the_previous_build(self):
        build(self.root)
        previous=(self.root/'_site/build-receipt.json').read_bytes()
        (self.root/'store/scene.py').write_text('def render():\n    return {"svg": None, "controls": "", "description": ""}\n')
        with self.assertRaisesRegex(ValueError,'svg, controls and description strings'):build(self.root)
        self.assertEqual((self.root/'_site/build-receipt.json').read_bytes(),previous)

    def test_scene_description_is_plain_text_and_all_slots_are_required(self):
        source=self.root/'store/scene.py'
        source.write_text('def render():\n    return {"svg": "<svg/>", "controls": "<button>Look</button>", "description": "<unsafe>& description"}\n')
        rendered=render_store(self.root)
        self.assertEqual(rendered.h1.get_text(),'<unsafe>& description')
        self.assertFalse(rendered.find('unsafe'))
        template=self.root/'store/page.html'
        template.write_text(template.read_text().replace('{{scene_controls}}',''))
        with self.assertRaisesRegex(ValueError,'one scene slot: controls'):render_store(self.root)

    def test_source_module_directories_cannot_be_replaced_by_a_build(self):
        for module in ('store','receipt'):
            with self.subTest(module=module):
                with self.assertRaisesRegex(ValueError,'source directory'):build(self.root,output=self.root/module)
                self.assertTrue((self.root/module/'page.html').is_file())


if __name__=='__main__':unittest.main()
