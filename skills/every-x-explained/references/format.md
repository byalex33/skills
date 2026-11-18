# Format spec — bold-caps "Every X Explained"

Measured from the reference videos (Aero Explained, Nov 2026), then changed on user feedback: the reference uses hard cuts and single-frame pops; ours keeps the look but moves smoothly (see Motion). Numbers are targets, not limits.

## Structure
- Item count and length are asked in step 1 (default 8 items, ~10 min). One chapter per item; words per chapter ≈ minutes × 155 ÷ items (best at 200–260 words, i.e. 60–100 s).
- No intro, no outro, no call to action. 0:00 is the first item's name; the video ends on the last item's closing line.
- Order: a punchy, dramatic story first; the biggest or most famous item last.
- Title `Every <X> Explained In <N> Minutes`, N = runtime rounded.

## Chapter shape (script)
1. **Hook**: the name, then an appositive with no main verb. *"WowAir. The airline that promised to fly you across the Atlantic for less than the price of a nice dinner."* / *"Sukhoi, the most recognizable name in Russian aviation and one that no longer technically exists."*
2. **Origin**: founded/designed when, where, by whom.
3. **What made it special**, with concrete numbers.
4. **The turn**: "But…", "Then…".
5. **Climax** with an exact date and hard numbers.
6. **Closer**: a quote, an irony, or a one-line verdict (*"The engineering is there. The scale and the market access are not."*).

Plain short sentences, active voice, many concrete figures, comparisons that make a number land. Light hedging ("around", "reportedly") where sources differ.

## Canvas
- 1920×1080, pure white, still images only. Beats change on a cut, but every element eases in (see Motion), so the cut never reads as a jump.
- Chapter label top-left on every frame of a chapter: tiny bold caps (build.py does this).
- 1–3 elements per frame. Images are plain rectangles on white, ~50–65% of frame width.

## The lineup
- One image of all items in a grid with labels (1 row up to 4 items, 2 rows up to 12). Chapter 1 opens on the full grid and zooms into item 1; every later chapter opens by panning the zoomed lineup to the next item while the name is spoken. Each chapter's first beat is `{"type": "lineup"}` and says only the name.
- Lineup images must match each other: side-profile drawings or cut-outs on white, same facing direction.

## Text (the bold-caps look)
- On-screen text is a **verbatim fragment** of the narration, upper case, heavy **Allo** (Black 900 for cards and captions, ExtraBold 800 for the chapter label, Bold 700 for lineup labels).
- One emphasis per frame at most: `{red:…}` for the key name/place/word, `{green:…}` for money, `{big:…}` for a year or single key word, combinations like `{big red:42}`.
- Text-only cards for dates, years, big numbers and single punch words ("BOTH DEALS", "1ST APRIL 2002").
- Headline above a photo (1–2 lines) or caption below it.

## Pacing
- A new visual about every 8 words (2–3 s). Nothing static for more than ~5 s.
- Lists: one beat per item (~0.5 s each).
- Builds: show the photo, then the same photo with a caption or pop in the next beat. When consecutive beats use the same image, the image stays put and keeps drifting; only the new parts animate in.

## Prop vocabulary
- Curved blue arrow: person→name, A→B (sold to, merged with, replaced by).
- `✅` success/yes, `❌` failed/not, `🛑` stopped/ceased, `🤝` deal/partnership, `💡` idea, `👉` pointing at a detail, `⭐` famous, flags for countries.
- Blur card (`blur_text`): one big phrase over the previous frame blurred.

## Motion (build.py adds all of this)
Motion is chosen by **meaning first, seed second**. The build log prints each beat's role and picks.

**Timing**
- Every visual starts 0.25 s **before** its first word (never within 0.3 s of the previous beat); the first move inside a beat starts ~0.1 s in.

**Roles** (from the beat's words and position)
| role | when | how it moves |
|---|---|---|
| turn | beat starts with But / However / Yet / Instead / Then / Until / Except | hard cut with a small jolt, no entrances, image stays still |
| climax | a full date (5th of March, 1936) or a big figure (20,000) — rare by design | fast (0.6×), `expo.out`, zoom-through scene, always a marker |
| closer | last beat before the next lineup | slow (1.5×), `sine.out`, gentle moves, often still |
| hook | first beat after the lineup | push-up scene entrance ("new section") |
| normal | everything else | seeded moves at 0.85–1.15× speed; push-left scene on ~1 in 6 |

**Vocabulary** (seeded inside the allowed set, never the same pick twice in a row)
- Image entrance: rise, slide-left, slide-right, zoom-out, drop, tilt, punch.
- Image drift: zoom-in, zoom-out, pan-left, pan-right, tilt, **still** (stillness is a move).
- Text entrance: rise, drop, pop, swing (per word), lines, zoom (per line). Total stagger ≤ 0.5 s; with word entrances the **key word lands first**, the rest follows.
- Emphasis: punch, stretch, shake (≤6 letters); hop, small shake (longer words).
- **Markers** on the key word, drawn after it lands: underline (blue brush stroke), circle (blue hand-drawn ellipse), highlight (yellow sweep behind the word). Always on a climax, ~1 in 3 elsewhere, rarely twice running.
- Count-up for figures with thousands separators (works with markers).
- Pops/emoji: bounce, spin, drop. Pairs: slide, pop, drop.
- Arrows draw on, then the filled head pops. Blur card background fades and settles.
- Lineup: smooth zoom/pan (power3 in-out, ≤1.3 s); a row change zooms out to the full grid and back.
- Render at 30 fps.

## Audio
- Voice only. No music, no sound effects.

## Review checklist (step 6)
- [ ] Every frame is white with 1–3 elements; nothing overlaps the chapter label.
- [ ] Every caption is words the narrator says in that beat.
- [ ] At most one coloured emphasis per frame.
- [ ] No image is stretched, watermarked, low-res (shown much smaller than its neighbours), or on a coloured box.
- [ ] Every element has finished its entrance before the beat ends (look at short beats).
- [ ] Each chapter starts on the lineup and the zoom lands on the right item.
- [ ] No beat under ~0.4 s except list items; none over ~5 s.
