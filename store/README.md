# Store interior

`/` is an original portrait cutaway of 57STORE. Everything visible belongs to the shop. Do not add a masthead, site footer, instructional floor text, floating navigation markers or hover-only information.

## Sources and layout

The entrance is at the **top**, so a phone enters from the front and scrolls deeper into the shop. The counter is beside the entrance, with a short bounded cashier workspace. Magazines face the front window; umbrellas and baskets stay to its side. Four central gondolas have front, middle and rear cross-aisles. Both side aisles are public. Coffee and waste sorting are separate from chilled dairy and the sliding-lid ice-cream freezer. Rice balls, sandwiches and bentos sit in open chilled cases along the opposite perimeter.

The drink display at the rear is a **walk-in cooler**, not a shallow cabinet pushed against an arbitrary wall. Behind its glass doors there are rear-access stock racks, an open replenishment aisle, boxed pre-chilled drinks and a circulating-air unit. A thick insulated swing door connects this room to the back stock room. The staff entrance opens from the public rear cross-aisle. The office desk is separated by a short wall with a doorway; its computer is the CCTV entry. The small camera above the front window is only a camera.

This is a compact fictional store, not a construction drawing or a traced floor plan. Equipment types and circulation were checked against:

- [Seven & i: store layout and merchandising](https://www.7andi.com/company/challenge/2751/2.html) — checkout circulation and grouped chilled/daily food.
- [Convenience Store Walker: photographed store renovation and before/after plans](https://cvs.main.jp/pictures/seven_layout_newformat/) — first-hand reference for front-window magazines, checkout, perimeter cases and open customer aisles; individual stores and generations differ.
- [Fukushima Galilei convenience-store equipment catalogue, pp. 38–39, hosted by distributor Fixwell](https://www.fixwell.com.hk/cfolder/fixwell/Library/Tree/04_PRODUCTS/01_REFRIGERATION/01_FUKUSHIMA_GALILEI/FIXWELL_-_Galilei_CV_v25.pdf) — open cases versus glass-door walk-in rooms, rear replenishment and reserve pre-cooling space.
- [Panasonic showcase product types](https://panasonic.co.jp/hvac-cc/biz/products/cold-chain/showcase/) — distinguish open chilled cases, reach-in cases and chest freezers.
- [Saint11: pixel clusters](https://saint11.art/pixel_art_articles/article2/), [shading](https://saint11.art/pixel_art_articles/article4/) and [animation timing](https://saint11.art/pixel_art_articles/article3/) — coherent silhouettes, limited colour clusters, consistent hard-edged light and stepped motion with pauses.

References inform the design; no reference photos, floor plans, tutorials or third-party sprites are shipped. The original drawing, palette adaptations, goods and motion are authored here. All three brand slogans are printed on the physical glazing transom. The floor and entrance mat carry no explanatory text.

## Module files

- `page.html`: semantic main, figure, three destinations, invisible descriptive alternative.
- `scene.py`: deterministic, layered, integer-coordinate SVG. Coordinate space is **640 × 1500**; no runtime renderer, external art service, framework or fetch.
- `config.json`: 3 route anchors and 32 compact inspection notes with authored hit areas. Descriptions represent fictional stock, not live inventory.
- `style.css`: room scaling, in-world feedback, compact notes and motion.
- `interactions.js`: tap/click/keyboard, note positioning and visibility-aware animation pausing.

The desktop width is capped at 800 CSS pixels. Mobile scales proportionally and scrolls vertically. Primary equipment/routes use at least 44 × 44 CSS pixel targets at 320px; five small props/people have at least 24px targets and do not overlap neighbouring controls. Keep bounds consistent with artwork. Related small items such as the sink/stock rack, lockers/clock and cooler fan/reserve crates share an inspection area.

## Interaction and animation

Inspection shows a **154px-wide non-modal note** beside the object, with one title and one short sentence. No overlay, inventory sheet, close button, focus trap or hover state. Tap again, tap elsewhere or press Escape to close. All 32 notes can be reached by keyboard. The receipt printer, SYS terminal and office CCTV computer remain ordinary links. Unmodified clicks briefly move paper or screen content before navigation; modified/new-tab clicks retain browser behavior. Keyboard focus illuminates the actual object rather than drawing a hit-box outline.

The motion designs are independent and deliberately unsynchronised:

1. Automatic door leaves slide into the side glazing.
2. Transom light subtly changes intensity.
3. Hot-food case light cycles gently.
4. Microwave display changes brightness.
5. Checkout display advances a line.
6. Printer paper feeds a few pixels.
7. Coffee steam rises and dissipates.
8. Entrance camera turns slightly on its bracket.
9. SYS screen types successive lines.
10. Fresh-case lights breathe softly.
11. Case glass catches a moving reflection.
12. Freezer edge light and ice reflection shift.
13. Drink-case lighting and door reflections vary.
14. Shopper walks within the central aisle with stepped feet.
15. Magazine reader turns a page.
16. Cashier moves a hand over the counter.
17. Rear worker reaches towards replenishment stock.
18. Cooler circulation fan rotates.
19. Office monitor scan line moves across its own screen.
20. Staff clock hand ticks.

A tapped shelf nudges its goods; a tapped screen advances its contents. CSS animates only small transforms/opacity regions. Off-screen fixtures and hidden tabs pause. No audio, network animation loop, GPU blur, video background or analytics.

`prefers-reduced-motion: reduce` disables all movement and link delays by default. For a **deliberately requested animated preview**, `?motion=on` enables motion in this tab and remembers it for that tab session; `?motion=off` clears the override. This exists because the desktop preview browser can inherit reduced motion. No global browser or OS setting is changed. Without JavaScript the complete illustration and all three destination links still work.

## Verification and review

Run the root README's Python checks and `pnpm test:browser` after building. Browser checks cover 320/390/768/1440px, every inspection note, all routes, target collisions, card bounds, keyboard dismissal, actual movement over time, reduced motion, the explicit opt-in and no-JS navigation. They capture mobile, desktop and opened-note previews.

`STORE_SCREENSHOTS` selects the screenshot directory; `STORE_SITE_DIR` selects the existing built output. In synced desktop folders use an output under `/tmp` to avoid sync-conflict copies:

```sh
python scripts/build.py --output /tmp/57store-preview
python scripts/check.py --output /tmp/57store-preview
STORE_SITE_DIR=/tmp/57store-preview pnpm test:browser
python -m http.server 8057 --bind 127.0.0.1 --directory /tmp/57store-preview
```

The branch and draft PR are for review. CI produces an offline site artifact and browser screenshots. Production publication is still controlled by the existing main-branch workflow; do not merge until the user approves the visual result.
