# "Every X Explained In N Minutes" — format analysis

Source videos (both from the channel **Aero Explained**):

| ID | Title | Length | FPS | Words | WPM | Visual changes | Avg per visual |
|---|---|---|---|---|---|---|---|
| `Z5dZ2V-4gtc` | Every Bankrupt Airline Explained In 10 Minutes | 9:44 (584 s) | 23.976 | 1,625 | ~167 | 192 | 3.0 s / ~8.5 words |
| `NDNSkVvetD0` | Every Military Aircraft Manufacturer Explained In 11 Minutes | 11:04 (664 s) | 30 | 1,947 | ~176 | 254 | 2.6 s / ~7.7 words |

"Visual changes" = ffmpeg `scene>0.3` hits. On a white canvas this fires on element pop-ins as well as full cuts, so read it as "something new appears every ~2.5–3 s / ~8 words", not as shot count.

Status legend: **[obs]** = observed in the files, **[guess]** = inference, not verified.

---

## 1. Shared format grammar (both videos)

### Macro structure
- **[obs]** Exactly **8 items**, each a chapter of **60–100 s** (~1:15 average). Chapters listed in the description as `TIMESTAMPS:` and picked up by YouTube as chapters.
- **[obs]** **No intro, no outro, no CTA, no sponsor read** in the video. It opens on the first item's name at 0:00 and ends hard on the last item's final line.
- **[obs]** Title pattern: `Every <Category> Explained In <N> Minutes`. N ≈ runtime rounded.
- **[obs]** Description: one-line title restatement, "Please like and subscribe…", `TIMESTAMPS:` block, long `DISCLAIMER:` paragraph. Airline video also has an affiliate link on line 1.
- **[obs]** Ordering looks deliberate: the biggest / most famous item is **last** (Pan Am, Lockheed Martin). The first item is a strong, punchy story (WOW air, Dassault).

### The "lineup" device (signature move)
- **[obs]** A **master lineup image**: all 8 items drawn side by side in a 4×2 grid on white, each with a label under it (airline video: side-profile plane in livery + airline name; military video: cartoon-style illustrated jet + manufacturer name, comic-style font).
- **[obs]** 0:00 opens on the full lineup, then **zooms in** onto item 1 over ~1.3 s while the narrator says the name.
- **[obs]** Every chapter boundary: cut back to the lineup (zoomed out briefly in the military video), then zoom/pan to the next item and hold ~1–1.5 s while the name is spoken. Then hard cut into the chapter.
- So the lineup = thumbnail-like table of contents + chapter divider + progress indicator in one asset.

### Canvas & layout
- **[obs]** Pure **white background** throughout. No video footage at all — 100% still images.
- **[obs]** **Persistent chapter label top-left** on every frame of the chapter (airline: tiny bold caps `WOW AIR`; military: italic `Dassault Aviation:`).
- **[obs]** Images are rectangular cut-outs (no frame/shadow) placed on white, usually ~50–70% of the frame width. Logos sit on white directly.
- **[obs]** Composition is "1–3 elements per beat": photo + caption, logo + emoji, flag + photo, logo → arrow → logo.

### Motion
- **[obs]** **Hard cuts only.** No crossfades, no slides between beats.
- **[obs]** Elements **pop in on a single frame** (no easing, no scale-up) — e.g. a green check mark appears on top of a photo, a handshake emoji appears next to a logo, a caption appears under a photo.
- **[obs]** When a second element arrives, the first one **jumps** (re-lays out) to make room — e.g. WOW logo centered → logo shifts left as the handshake appears.
- **[obs]** Builds within a beat: photo → +arrow → +caption → +second line of caption (text accumulates on screen over 2–4 sub-beats).
- **[obs]** Only real camera move is the lineup zoom/pan.
- **[obs]** One-off trick: big text word over a **heavily blurred copy of the previous frame** ("ATLANTIC" over blurred WOW logo + handshake).

### Pacing / sync
- **[obs]** A new visual on nearly every **noun phrase or idea**: name → logo; place → map/photo; year → big year text; person → portrait; number → big number text.
- **[obs]** **Lists get one visual per item at ~0.5 s each** (Egypt, Qatar, India, Greece… each with its own flag+jet).
- **[obs]** Cuts land in the **pauses between phrases** (audio energy at cut points is lower than at random points in the airline video).
- **[obs]** Narration is tight: very few silences >0.25 s; pauses look trimmed.

### Iconography toolkit (recurring props)
- Curved **blue arrows** (pointing from text to image, or logo → logo for "sold to / merged with").
- **Emoji** (Apple-style): handshake = deal/partnership, pointing hand, lightbulb = idea, raised hand = "but".
- Green **check mark** = success / yes; red **X** in a circle over a logo/map = failed / not.
- **STOP sign** = ceased operations.
- **Country flags** for nationality, often next to a photo of the item.
- Departure board showing CANCELLED, newspaper headlines, money photos, calculators = stock "concept" photos.

### Audio
- **[obs]** Single **voiceover**, no continuous music bed (quietest 5% of the track sits around −70 dBFS, i.e. near silence between phrases).
- **[obs]** No detectable whoosh/pop SFX on cuts (high-frequency energy at cuts is not higher than at random points).
- **[guess]** Voice may be TTS (very even delivery; transcript has an artefact "So, So,"). Could also be a human read edited tightly. Unverified.

### Script style
- **[obs]** Each chapter opens with a **name + appositive hook**, no verb: *"WowAir. The airline that promised to fly you across the Atlantic for less than the price of a nice dinner."* / *"Dassault Aviation, France's fighter manufacturer and the only company in Europe that still…"* / *"Sukhoi, the most recognizable name in Russian aviation and one that no longer technically exists…"*
- **[obs]** Then: origin (founded when/where/by whom) → what made it special → the turn ("But…", "Then it started winning them.") → the climax with a **specific date** and **hard numbers** → a closing line that is a quote, irony or a one-sentence verdict (*"The engineering is there. The scale and the market access are not."*).
- **[obs]** Short, plain sentences; lots of concrete numbers (dates, $ amounts, headcounts, production rates); comparisons to make numbers land ("roughly the same number DASO has built of the Rafale in total").
- **[obs]** ~200–260 words per chapter.
- **[obs]** Light hedging ("reportedly", "around", "estimates vary") + the description disclaimer.

---

## 2. Variant A — "Bold caps" (bankrupt airlines video) — **CHOSEN TARGET (2026-11-17)**

- On-screen text = **verbatim fragments of the narration**, in **heavy geometric sans, ALL CAPS, black** (looks like Montserrat Black/ExtraBold **[guess]**).
- **Key word emphasis**: one word bigger (`2011`, `CENTURY`, `MARCH`, `DEALS`), or coloured **red** (`REYKJAVIK`, `INVESTMENT`, `LATE 1990s`, `17,000`) or **green** for money (`$500 MILLION`).
- Text often the **whole visual** (text card on white) for dates/years/single words.
- Text placed **above** the photo as a 1–2 line headline, or **below** as a caption ("FORGIVE HIMSELF / FOR NOT ACTING SOONER").
- Chapter label: tiny bold caps top-left.
- More concept stock photos and emoji; feels like a kinetic-typography explainer.

## 3. Variant B — "Annotated notebook" (military manufacturers video)

- On-screen text = **paraphrased lowercase labels**, not verbatim: "built by multiple countries", "walked away from this", "it wanted this", "then it started winning them…", "cost €45.9 billion to build".
- Font: **italic Helvetica/Arial-like**, small, black **[guess on exact font]**. Some labels are tiny photo credits ("Royal Air Force Eurofighter EF-2000 Typhoon F2").
- **Thin light-blue hand-drawn-style arrows** connecting label → image, image → flag, logo → logo; straight blue block arrows for "leads to".
- More **diagram-like** compositions: logo + map + arrow + photo; four flags in a row with handshake emojis between them; 2×2 grids of photos; "=" signs ("= flying control tower", "= £8 to £10 billion a year").
- Chapter label: italic `Name:` top-left.
- Calmer, "explained on a whiteboard" feel; fewer emoji.

---

## 4. Beat-level examples

Full tables: `reference/wow_ch1_beats.txt`, `reference/dassault_ch1_beats.txt` (each visual change + the words spoken during it).

WOW air, first 20 s (visual from contact sheets):

| t | Narration | Visual |
|---|---|---|
| 0.0 | "WowAir." | Lineup strip zooming in to WOW air plane + label |
| 1.3 | "The airline that promised to fly you…" | WOW logo centered → handshake emoji pops in, logo jumps left |
| ~3.8 | "…across the Atlantic…" | `ATLANTIC` over blurred previous frame, then `PRICE OF DINNER` added |
| 6.4 | "founded in Iceland in 2011 by" | Plane photo → arrow + `ICELAND 2011` (2011 bigger) |
| 9.2 | "an entrepreneur called Skúli Mogensen" | Arrow + `SKÚLI MOGENSEN` + portrait |
| 11.6 | "started flying in 2012. The idea was simple." | `2012` + plane over sky → `SIMPLE` + pointing hand + lightbulb |
| 15.1 | "…between North America and Europe" | Plane photo → `NORTH AMERICA` ↷ `EUROPE` above it |
| 19.1 | "with a quick stop in Reykjavik" | Caps headline (REYKJAVIK red) over aerial city photo |
| 21.2 | "fares as low as $99" | Screenshot of fare grid, $99 circled |

---

## 5. What the skill will need to produce (draft, for discussion)

1. **Topic → 8 items** + ordering (strong opener, biggest last).
2. **Script**: ~8 × 220 words, hook-appositive opener, dated climax, verdict closer. Fact-checked.
3. **Beat sheet**: split script into ~8-word beats; per beat pick a visual type (logo / photo / text card / flag / emoji / arrow / map / number) and layout.
4. **Assets**: lineup image (8 items, consistent style), logos, photos, flags, emoji, arrows.
5. **Voiceover** with word timestamps.
6. **Render**: white 1920×1080 canvas, hard cuts on beat boundaries, single-frame pop-ins, lineup zoom at chapter starts, chapter label top-left.
7. **Description** with timestamps + disclaimer; title in the `Every X Explained In N Minutes` pattern.

Open questions for the user are listed in `PROCESS_LOG.md`.
