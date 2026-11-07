# Store interior

The root route is one self-contained, code-drawn room. There are no downloaded
sprites, raster textures, scene images, remote fonts, browser 3D engine or
production JavaScript dependencies.

- `plan.py`: metre-space layout, fixtures, small inspection notes, two routes.
- `shop.py`, `back.py`: original solid geometry for merchandise, equipment and people.
- `mesh.py`: fixed eight-colour palette, parallel projection, pixel snapping,
  depth ordering and removal of completely concealed stationary surfaces.
- `scene.py`: semantic controls generated from the same objects as the artwork.
- `page.html`, `style.css`, `visit.js`: standalone page, physical motion and taps.

The upper entrance leads to checkout, baskets, umbrellas and a wall magazine
rack. Three double-sided rows have continuous public aisles on both sides.
Cold cases follow the east wall. The rear public aisle reaches the toilet and
a separate employee door. A service passage connects the one compact staff
room and the cold room behind the rear-stock drink cabinet. The left-hand
internal computer opens SYS, whose module selection also opens CCTV. The
right-hand wall holds three six-door locker banks. Walls are cut away for
visibility; their floor contacts remain in the same three-dimensional
coordinate system as the equipment.

Brand lettering and the three slogans are woven into the entrance mat. Other
floor surfaces contain no explanatory text. Tap objects for a short local note;
the receipt printer and the single internal SYS screen are the two page destinations.

## Motion and access

Seventeen named motion hooks cover the sliding doors, sensor, POS text, receipt
paper, hot-case lamp, coffee steam, case lights, glass reflections, drink lights,
camera head, cold-room fan, SYS typing, kettle steam, and small human
movements. Offscreen and hidden-page activity pauses. The operating system's
reduced-motion preference disables them. A deliberate `?motion=on` preview
choice enables motion and is remembered locally; `?motion=off` clears it.
No permanent settings panel or decorative site chrome is added to the room.

Inspection cards support touch, keyboard, Escape and outside-tap dismissal.
They stay within the current viewport. Both route links work without
JavaScript. Inspectable controls are revealed only after their handlers exist.

## Build and browser checks

Use the root Python requirements. Build outside the source tree if the checkout
is in a cloud-synced folder:

```sh
python scripts/build.py --output /tmp/57store-preview
python scripts/check.py --output /tmp/57store-preview
npm ci --ignore-scripts
npx playwright install chromium
STORE_PREVIEW_DIR=/tmp/57store-preview npm run test:store
python -m http.server 8057 --directory /tmp/57store-preview
```

The browser checks exercise 320, 375, 768 and 1440px widths, every inspection,
keyboard access, real navigation, no-JavaScript links and reduced-motion
choices. CI also builds a project-path preview. No preview job deploys Pages.

## Construction references

Fresh physical reference photographs and diagrams informed construction only;
no reference art ships with the scene. Consulted sources include FamilyMart's
Famima concept/store photographs, Lawson's equipment/energy pages, Okamura
retail gondola and book racks, Fuji FCMD300ML coffee equipment, Panasonic
NE-1802 microwaves, Toshiba WILLPOS A20, SDRS cold cases, TOTO toilet/small-room
construction guidance and EIZO T966 front/side drawings. Their fixture designs
were reduced to original neutral geometry in the site's own palette.
