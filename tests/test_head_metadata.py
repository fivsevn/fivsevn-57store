from pathlib import Path
import sys
import unittest
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import build, SITE_URL
from site_post_metadata import read_frontmatter, dump_frontmatter
from head_metadata import add_missing_metadata, metadata_head
import test_build as fixtures


class HeadMetadataTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BuildTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        (self.root / 'toilet/index.html').write_text('<!doctype html><html><head><title>Toilet</title><meta name="description" content="Preserved description"><link rel="canonical" href="'+SITE_URL+'/toilet/"></head><body><p>Unchanged experiment.</p></body></html>')
        (self.root / 'pi5/57store/system/static/index.html').write_text('<!doctype html><html><head><title>Pi snapshot</title></head><body>Unchanged snapshot.</body></html>')

    def test_public_pages_and_new_entries_have_metadata_and_a_canonical_sitemap(self):
        self.fixture.post('sys', 'new-entry', '2026-06-08T21:00:00+08:00', body='A **new** system note.')
        self.fixture.post('sys', 'private-entry', '2026-06-08T22:00:00+08:00', visibility='private')
        build(self.root, base_path='/preview')
        public = set()
        for file in (self.root / '_site').rglob('*.html'):
            page = BeautifulSoup(file.read_text(), 'html.parser')
            for selector in ('meta[name="description"]', 'link[rel="canonical"]', 'meta[property="og:title"]',
                             'meta[property="og:description"]', 'meta[property="og:url"]', 'meta[property="og:type"]',
                             'meta[name="twitter:card"]', 'meta[name="twitter:title"]', 'meta[name="twitter:description"]'):
                self.assertEqual(1, len(page.head.select(selector)), (str(file), selector))
            canonical = page.select_one('link[rel="canonical"]')['href']
            self.assertTrue(canonical.startswith(SITE_URL + '/'))
            self.assertNotIn('/preview/', canonical)
            self.assertEqual(canonical, page.select_one('meta[property="og:url"]')['content'])
            self.assertEqual(page.title.get_text(), page.select_one('meta[property="og:title"]')['content'])
            if not page.select_one('meta[http-equiv="refresh"]'):
                public.add(canonical)
            image = page.select_one('meta[property="og:image"]')
            if image:
                self.assertTrue((self.root / '_site' / unquote(urlparse(image['content']).path).lstrip('/')).is_file())
        detail = BeautifulSoup((self.root / '_site/sys/new-entry/index.html').read_text(), 'html.parser')
        self.assertEqual('A new system note.', detail.select_one('meta[name="description"]')['content'])
        self.assertEqual('article', detail.select_one('meta[property="og:type"]')['content'])
        tree = ElementTree.fromstring((self.root / '_site/sitemap.xml').read_text())
        locations = [node.text for node in tree.findall('{*}url/{*}loc')]
        self.assertEqual(public, set(locations))
        self.assertEqual(len(locations), len(set(locations)))
        self.assertFalse(tree.findall('.//{*}lastmod'))
        self.assertFalse(any('private-entry' in location or '/cache/page/2/' in location for location in locations))
        self.assertIn('Sitemap: '+SITE_URL+'/sitemap.xml', (self.root / '_site/robots.txt').read_text())
        retained = BeautifulSoup((self.root / '_site/toilet/index.html').read_text(), 'html.parser')
        self.assertEqual('Preserved description', retained.select_one('meta[name="description"]')['content'])

    def test_summary_escaping_and_enrichment_keep_body_bytes_and_existing_tags(self):
        path = self.root / 'sys/2026/06/sys-0/index.md'
        meta, body = read_frontmatter(path)
        meta['title'] = '<title> & "quoted" </title><script>alert(1)</script>'
        meta['summary'] = 'Summary <field> & "quote".'
        path.write_text(dump_frontmatter(meta) + body)
        build(self.root)
        detail = BeautifulSoup((self.root / '_site/sys/sys-0/index.html').read_text(), 'html.parser')
        self.assertEqual(meta['summary'], detail.select_one('meta[name="description"]')['content'])
        self.assertEqual(1, len(detail.head.select('meta[name="description"]')))
        self.assertFalse(detail.head.find('script'))
        original = '<html><head><title>Kept</title><meta name="description" content="Kept"></head><body> exact\n<script>let x = 1;</script></body></html>'
        tags = metadata_head('Kept','Generated',SITE_URL+'/test/',site_name='57store')
        enriched = add_missing_metadata(original,tags)
        self.assertEqual(original.split('</head>',1)[1],enriched.split('</head>',1)[1])
        self.assertEqual(enriched,add_missing_metadata(enriched,tags))
        self.assertEqual('Kept',BeautifulSoup(enriched,'html.parser').select_one('meta[name="description"]')['content'])


if __name__ == '__main__':
    unittest.main()
