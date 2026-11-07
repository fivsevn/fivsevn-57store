"""Check visible geometry results rather than the renderer's sorting internals."""
from pathlib import Path
import runpy
import unittest
from xml.etree import ElementTree

from bs4 import BeautifulSoup


ROOT=Path(__file__).resolve().parents[1]
COLORS={'#090b0c','#131415','#252a2d','#4c595e','#8a999a','#c6d0ca','#edf1e7','#55efc1'}


def polygons(svg):
    """Read the SVG's actual document paint order and owning object labels."""
    result=[]
    def walk(element,owner=None):
        owner=element.get('data-owner',owner)
        if element.tag.rsplit('}',1)[-1]=='polygon':
            points=[tuple(map(float,pair.split(','))) for pair in element.get('points').split()]
            result.append((owner,points,element.get('fill')))
        for child in element:walk(child,owner)
    walk(ElementTree.fromstring(svg))
    return result


def covers(points,sample):
    """Independent even-odd hit test for a sample safely inside a face."""
    x,y=sample;inside=False
    previous=points[-1]
    for current in points:
        ax,ay=previous;bx,by=current
        if (ay>y)!=(by>y) and x<ax+(y-ay)*(bx-ax)/(by-ay):inside=not inside
        previous=current
    return inside


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        engine=runpy.run_path(str(ROOT/'store/mesh.py'))
        cls.Scene=engine['Scene']
        cls.project=staticmethod(engine['project'])

    def test_long_shelf_does_not_cover_a_raised_product_at_its_far_end(self):
        # The shelf runs far into the room. Its average distance exceeds the
        # product's, although the product sits above it on their shared ray.
        for order in [('shelf','product'),('product','shelf')]:
            with self.subTest(insertion_order=order):
                scene=self.Scene()
                for owner in order:
                    model=scene.model(owner,0,0)
                    if owner=='shelf':
                        model.quad([(0,0,1),(2,0,1),(2,12,1),(0,12,1)],'steel',double=True)
                    else:
                        model.quad([(.5,.45,1.4),(1.2,.45,1.4),(1.2,.95,1.4),(.5,.95,1.4)],'mint',double=True)
                sample=self.project((.85,.70,1.4))
                painted=[(owner,color) for owner,points,color in polygons(scene.svg()) if covers(points,sample)]
                self.assertTrue(painted)
                self.assertEqual(painted[-1],('product','#55efc1'),'The raised product must remain the visible top surface')

    def test_only_an_opaque_stationary_wall_discards_the_concealed_object(self):
        for opacity,motion,retained in [(1,None,False),(.25,None,True),(1,'door-l',True)]:
            for order in [('wall','product'),('product','wall')]:
                with self.subTest(opacity=opacity,motion=motion,insertion_order=order):
                    scene=self.Scene()
                    for owner in order:
                        model=scene.model(owner,0,0)
                        if owner=='wall':
                            if motion:model=model.part('sliding-leaf',motion)
                            model.quad([(0,6,0),(3,6,0),(3,6,4),(0,6,4)],'steel',opacity=opacity,double=True)
                        else:
                            model.quad([(.6,4,.7),(1.1,4,.7),(1.1,4,1.3),(.6,4,1.3)],'mint',double=True)
                    owners=[owner for owner,_,_ in polygons(scene.svg())]
                    self.assertEqual('product' in owners,retained)
                    self.assertIn('wall',owners)
                    if retained:
                        self.assertLess(owners.index('product'),owners.index('wall'),'Glass or the sliding leaf must composite over the retained object')

    def test_repeated_rendering_keeps_the_same_painted_geometry_and_ids(self):
        scene=self.Scene()
        shelf=scene.model('shelf',0,0)
        shelf.box(0,0,0,2,6,.8,'steel')
        moving=shelf.part('paper-slip','paper-feed')
        moving.quad([(.5,.4,.81),(.8,.4,.81),(.8,.7,.81),(.5,.7,.81)],'paper',double=True)
        product=scene.model('product',0,0)
        product.box(.5,.8,.8,.3,.3,.4,'mint')
        first=scene.svg()
        self.assertEqual(first,scene.svg())
        svg=ElementTree.fromstring(first)
        identifiers=[element.get('id') for element in svg.iter() if element.get('id')]
        self.assertEqual(len(identifiers),len(set(identifiers)))
        self.assertTrue(polygons(first))


class FullStoreSceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=runpy.run_path(str(ROOT/'store/scene.py'))['render']()
        cls.svg=ElementTree.fromstring(cls.output['svg'])
        cls.controls=BeautifulSoup(cls.output['controls'],'html.parser')

    def test_full_artwork_uses_only_the_fixed_palette_and_unique_object_ids(self):
        identifiers=[];colors=set()
        for element in self.svg.iter():
            if element.get('id'):identifiers.append(element.get('id'))
            self.assertNotIn(element.tag.rsplit('}',1)[-1],{'image','img','foreignObject','script','iframe'})
            for attribute in ('fill','stroke'):
                if element.get(attribute):colors.add(element.get(attribute))
            self.assertFalse(any(attribute.rsplit('}',1)[-1] in {'href','src'} for attribute in element.attrib),'Artwork must not fetch image resources')
        self.assertGreater(len(identifiers),20)
        self.assertEqual(len(identifiers),len(set(identifiers)))
        self.assertTrue(colors)
        self.assertLessEqual(colors,COLORS)
        self.assertFalse(self.controls.select('img, image, iframe, script'))

    def test_full_scene_has_exactly_the_three_requested_destinations(self):
        anchors=self.controls.select('a[href]')
        self.assertEqual(len(anchors),3)
        self.assertEqual({anchor['href'] for anchor in anchors},{'/receipt/','/sys/','/cctv/'})
        self.assertTrue(all(anchor.get('aria-label','').strip() for anchor in anchors))
        self.assertTrue(self.output['description'].strip())


if __name__=='__main__':unittest.main()
