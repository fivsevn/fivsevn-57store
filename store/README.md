# Store interior

The root `/` is a complete, original, portrait cutaway of the convenience store. Everything visible belongs to the room: signs are on fixtures, navigation is through devices, and inspection opens stock labels. Do not add a site masthead, explanatory captions, floating numbered markers, status dashboard or footer around the scene.

- `page.html`: semantic main/figure, three page entries and inspection controls.
- `scene.py`: deterministic integer-coordinate SVG renderer. Edit the actual equipment and stock here. No remote assets or image-generation service is required.
- `config.json`: the three allowed destinations and six authored product labels. These are fictional store contents, not live stock levels. Keep product descriptions consistent with the drawing.
- `style.css`: layout, hit surfaces, physical label styling, object feedback and reduced motion.
- `interactions.js`: click/tap/keyboard interaction. No hover handlers, tracking, API calls or runtime data fetches.

## Layout and movement

The entrance is at the front/bottom. Customers have a clear entrance apron and can move through a front cross-aisle, along either side of the two double-sided gondolas, and across the rear drink aisle. The checkout queue stays to the left of the entrance. Fresh food runs along the right wall. The rear room contains replenishment stock, a sink, lockers and an office; the left staff passage connects it to the rear of the counter without crossing the queue. Appliances sit behind the cashier, with the hot-food display on the counter. The SYS station is accessible from the front public aisle.

Reference: [Seven & i — store layout and merchandising](https://www.7andi.com/company/challenge/2751/2.html) discusses wider checkout circulation and grouping daily/chilled food. This is an original compact layout informed by those circulation principles, not a reproduction of that plan or the supplied style reference.

The scene uses a `640 × 1040` authoring coordinate system and a cropped `viewBox="26 26 586 924"`. A position `(x, y)` maps to `left=(x−26)/586`, `top=(y−26)/924`. The desktop scene width is capped at 780 CSS pixels. Narrow screens scale proportionately, scroll normally and retain at least 44 × 44 CSS pixel hit areas. Recheck overlap whenever equipment or hit positions change.

## Interactions

- Printer, terminal and monitor are ordinary anchors. Unmodified clicks allow 220 ms of physical feedback before navigating; modifier clicks retain browser behavior. Reduced motion navigates immediately.
- Shelf and cooler controls show a native dialog styled as a printed store label. Close via the × button, Escape or a tap outside the paper. Focus returns to the inspected object. They never create routes to other modules.
- Screen feedback moves the screen contents. Printer feedback moves the paper. Shelf feedback moves goods, with no rectangular hover/click outline. Keyboard focus highlights the actual fixture.
- The single ambient shopper moves only within the center aisle. No clocks, live shifts or stock events are inferred from repository data in this prototype.

## Verify

From the repository root, run the documented Python checks and `pnpm test:browser` after building. The latter starts and stops its own local server. It writes desktop/mobile screenshots plus an opened stock-label screenshot to `test-results/`. `STORE_SCREENSHOTS` can point to another output directory; `STORE_SITE_DIR` selects an existing build outside `_site/`. On synced desktop folders, use an output under `/tmp` to avoid sync-conflict copies during rebuilds.

Changing store files does not change the original receipt or the retained archive styles. Production remains controlled by the existing main-branch deployment workflow.
