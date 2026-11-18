# Process log — analysing reference videos

Everything done in session 1 (2026-11-17), in order, with what went wrong. This is the raw material for the skill's "analyse a reference video" step.

## Environment found
- `ffmpeg` / `ffprobe` 9.0.2 (Homebrew) — present, but **built without `drawtext`** (no text overlays / timestamp burn-in).
- `python3` present. No `yt-dlp`, no `whisper`.

## 1. Install yt-dlp
```bash
brew install yt-dlp        # got 2026.10.26
```

## 2. Download
First attempt (videos + subs in one call) **failed for the videos**: YouTube returned `HTTP Error 429: Too Many Requests` on the `en` subtitle track, and yt-dlp aborted that video. The `en-orig` (auto-caption) track did download.

Working approach — two passes:
```bash
# pass 1: subtitles only (en-orig has word-level timing)
yt-dlp --skip-download --write-auto-subs --sub-langs "en-orig" --sub-format vtt -o "%(id)s.%(ext)s" URL...
# pass 2: video + metadata, -i so one failure doesn't stop the rest
yt-dlp -i -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 --write-info-json -o "%(id)s.%(ext)s" URL...
```
- `.info.json` gives title, description, chapters, duration, fps.
- Downloads went into their own folder (untrusted data), scripts in a separate folder.
- Videos (~180 MB) are kept in the session scratchpad only; re-download if needed.

## 3. Transcript
`tools/vtt2txt.py file.en-orig.vtt` — de-duplicates YouTube's rolling captions into timed lines.
- Note: `wc -w` on that output over-counts (timestamps). Count with `cut -d' ' -f2- | wc -w`.
- Auto-captions mangle names (DASO = Dassault, Sukcoy = Sukhoi, Loheed = Lockheed).

## 4. Visual change detection
```bash
ffmpeg -i in.mp4 -vf "scale=320:-1,select='gt(scene,0.3)',showinfo" -an -f null - 2>&1 \
  | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 > cuts.txt
```
On a white-canvas video this also catches element pop-ins; some double hits (0.03 s apart).

## 5. Contact sheets (how I "watched" the videos)
```bash
# opening 60 s, 1 frame / 2 s
ffmpeg -t 60 -i in.mp4 -vf "fps=1/2,scale=400:-1,tile=5x6:padding=4" -frames:v 1 open.jpg
# whole video, 1 frame / 12 s
ffmpeg -i in.mp4 -vf "fps=1/12,scale=400:-1,tile=5x10:padding=4" -frames:v 1 full.jpg
# motion study: native frame rate for 1 s
ffmpeg -ss 2.9 -t 1 -i in.mp4 -vf "scale=320:-1,tile=6x4:padding=3" -frames:v 1 native.jpg
```
No `drawtext`, so time = grid index × interval.
Lesson: 5 fps is too coarse to judge animation; use native fps for ~1 s around a transition.

## 6. Beat table
`tools/beats.py cuts.txt file.en-orig.vtt START END` — uses word-level `<c>` timings in the VTT to print each visual change with the words spoken during it.

## 7. Audio checks
- `volumedetect` + 5th-percentile RMS (~−70 dBFS) → no music bed.
- `tools/sfxcheck.py cuts.txt audio.raw` (16 kHz mono s16le from ffmpeg) → compares high-frequency energy just after cuts vs random times → no whoosh/pop SFX.

## Outputs
- `ANALYSIS.md` — the format breakdown.
- `reference/` — transcripts, cut lists, beat tables, contact sheets, info.json.
- `tools/` — the three Python helpers.

## Decisions (user feedback)
- 2026-11-17: **Target variant A "bold caps"** (airline video style). Variant B is reference only.
- 2026-11-17: **Images** = web search + download (real logos/photos; lineup assembled from cut-outs).
- 2026-11-17: **Voice** = ElevenLabs TTS (need word timings for cut sync). **Voice ID: `ynTHHllfDmGsZ3G8QJt9`** (user-specified).
- 2026-11-17: **Renderer** = **Hyperframes** (confirmed by user after asking about Hyperframes vs Remotion). Single renderer; Remotion only as a later fallback if Hyperframes can't do something.
- 2026-11-17: **Topics** = aviation and WW2 for now.
- 2026-11-17: **Do not use the `brag` plugin.** User asked to remove it: files moved to Trash (Finder), then `claude plugin uninstall brag@brag` + `claude plugin marketplace remove brag`. Hyperframes is not installed globally, so the skill must install/run it itself (e.g. via npx) — the earlier "already set up" argument no longer holds.

## Open questions for the user
All five answered on 2026-11-17 (see Decisions).
1. ~~Which variant to target~~ → answered: A "bold caps".
2. How should images be sourced (web search + download, AI image generation, user-supplied, or a mix)? The lineup image especially.
3. What produces the voice (ElevenLabs / other TTS, or the user records it)?
4. What renders the video (ffmpeg-only, Remotion, Hyperframes, Python/MoviePy, other)?
5. Topic scope: aviation only (like the channel) or any "Every X explained" topic?

---

# Session 1, part 2 — building the skill (2026-11-17)

Skill installed at `~/.claude/skills/every-x-explained/` (SKILL.md, references/format.md, references/beats-format.md, scripts/build.py, scripts/commons.py). Test slice in `slice-ww2/` (Spitfire chapter + Bf 109 opener, 48.5 s): `slice-ww2/slice-ww2-v3.mp4`.

## What was proven in the slice
- **Voice**: ElevenLabs connector `creative_generate_speech`, voice `ynTHHllfDmGsZ3G8QJt9`, `eleven_multilingual_v2`, 1 generation. Estimate 759 credits ≈ $0.15 for 47 s (→ ~$2 per 10-min video). `creative_get_generations` gives a signed `full_res_url` MP3 that `curl` downloads.
- **Timings**: `hyperframes transcribe narration.mp3 --language en` (whisper small.en, installs runtime on first use, ~25 s) → `transcript.json` word list.
- **Alignment**: build.py matches script tokens to ASR tokens with difflib and interpolates the rest → 96% matched; rendered cut times match planned beat starts within one frame.
- **Images**: Wikimedia Commons API works; bursts get HTTP 429 → added retry/back-off. Short queries (2–4 words) work, long ones return nothing. `"<name> profile"` finds side-profile drawings on white (good lineup images).
- **Render**: Hyperframes 0.9.59, GSAP only for the lineup zoom/pan; one static clip per beat = hard cuts. First render 1m57 (browser setup), later ones ~14 s for 48 s.
- **Fonts**: Montserrat via Google Fonts link loads in render. Apple emoji fail `check` (no font in cloud/Docker render) → switched to Twemoji SVGs fetched into assets/ by build.py.
- `mix-blend-mode: multiply` on images removes off-white JPEG box edges on the white canvas.
- build.py also writes `description.txt` (timestamps + disclaimer + Commons credits).

## Later fixes (after advisor review)
- `mix-blend-mode: multiply` also darkened the emoji pops → excluded `.pop` and `.emoji`.
- 8-item lineup tested (no voice cost, reused slice audio): tall images overflowed when zoomed → image height capped by cell width; a pan from row 1 to row 2 crossed blank space → row changes zoom out to the full grid and back in.
- Audio join (`ffmpeg concat` + `libmp3lame`) tested on two copies of the slice MP3: works.
- Not yet proven: a full 8-chapter, ~10-minute run (alignment over ~1,800 words, ~230 clips, render time).

## Problems hit
- Nested markup `{big:{red:42}}` did not parse → syntax is `{big red:42}`.
- First Bf 109 drawing had a blue background → replaced with a white-background colour profile.
- `hyperframes check` "craft" warnings on the tiny chapter label → `data-layout-ignore`. Studio-structure warnings (nested clips, track density) remain and are harmless for rendering.

## Open questions for the user (after slice)
1. Feedback on the slice look and pacing.
2. WW2 images with period markings (swastika on Bf 109 tail): keep accurate profiles, or avoid/crop them (YouTube ad-suitability)?
3. Should the skill stop for approval after the item list and after the script (current design), or run straight through?

## Feedback round 1 (2026-11-17, after slice v3)
- **Period markings: keep accurate WW2 images** (swastikas on aircraft are fine).
- **Add more animation: "nice and smooth".** The format moves away from the reference's hard cuts + single-frame pops toward eased entrances, slow push-ins and animated props, while keeping the white bold-caps look.
- Note: from here `dev/PROCESS_LOG.md` in the skill folder is the master copy; the session folder's research/ copy is frozen.

## Motion pass (2026-11-17) → slice v4
- Added `motion()` to build.py: eased image entrances + slow push-in (carried across repeated images), word-by-word text with punch on emphasis, arrow draw-on (pathLength=1 + strokeDashoffset tween; passes Hyperframes motion check), emoji/pop bounce, pair slide-ins, blur fade. Lineup ease power3.inOut, ≤1.3 s. Render 30 fps.
- Blur card copies the previous frame's HTML: motion classes are renamed inside the copy so it stays static.
- Pair layout overflowed the frame with the push-in → pair images max 640 px, push-in 2.5%.
- **Arrows (user feedback: "the arrows need work")**: the chevron head was misaligned with the curve end. The end tangent of the Bézier is steeper than what the eye reads, so a tangent-aimed chevron looked twisted and its lower arm read as a stub. Final design: filled isosceles triangle head (30 ahead / 10 behind the line end, half-width 16) aimed along the chord from t=0.8 to the end, covering the line end.
- Low-res Commons images (e.g. 624 px) display small → SKILL.md now asks for ≥1200 px files.
- Render: 48.5 s at 30 fps in ~22 s.

## Feedback round 2 (2026-11-17): "it seems it's just using the same motion over and over again" → slice v5
- Replaced the single preset with a motion vocabulary in build.py: 7 image entrances, 5 drifts, 6 text entrances, 3 emphasis (+2 soft ones for long words), 3 pop entrances, 3 pair styles, 3 occasional scene entrances, plus count-up for figures like 20,000.
- Picks are seeded per beat (`random.Random("beat-<i>")`), never repeat the previous beat's pick, and can be forced per beat with `"motion": {...}` in beats.json. build.py prints the picks per beat.
- Count-up uses a GSAP tween on a plain object with onUpdate writing textContent (deterministic on seek; passes check). The word gets a fixed min-width + tabular numerals so the line does not jitter.
- Bugs found and fixed: (1) blur-card static copy renamed `imgbox`→`imgbox-s`, but targets are found by substring, so the motion layer still saw an image → renamed to non-prefix names (`sbox`, `s-arline`, …). (2) "stretch" and "punch" on a long word (PROTOTYPE) covered the next word → long words (>6 letters) only get "hop" (vertical) or a small shake.
- User approved slice v5 motion variety ("Yes, looks good"), 2026-11-17. Next milestone: first full 8-chapter video (untested at full length).

## Feedback round 3 (2026-11-17): font → Allo
- User: use Allo (github.com/joshpuckett/allo); no new test video needed.
- Allo is SIL OFL 1.1. Downloaded Allo-Bold/ExtraBold/Black.woff2 + OFL.txt into `assets/fonts/`, verified against the repo's SHA256SUMS.
- build.py: removed the Google Fonts (Montserrat) link; local `@font-face` for weights 700/800/900; fonts copied into each project's `assets/fonts/`. Verified with build + `hyperframes check` (0 errors, no font findings) + 3 snapshot frames showing Allo glyphs. No MP4 re-rendered.

## Research: herk-edit-kit (github.com/nateherkai/herk-edit-kit, MIT, 2026-11-17)
Talking-head editing kit (silence/mistake cuts, lower thirds, captions, 406 motion cards, Hyperframes). Read: hyperframes/references/{motion-principles,transitions,dynamic-techniques,typography}.md, house-style.md, hyperframes-video-beats/SKILL.md, make-a-video/references/build-checklist.md, motion-showreel/scripts/sfx.mjs.

Tips that fit our format (not yet applied; awaiting user choice):
1. **Lead the word**: start a visual 0.2–0.6 s before its anchor word; zero-delay feels like a jump cut. Ours starts exactly on the word.
2. **Motion by meaning, not only by seed**: hard cut (no entrance) for disruption ("But…"), fast/expo for the climax (date, big number), slow/sine for the chapter closer. One primary transition (60–70%) + 1–2 accents instead of uniform random.
3. **Vary speed, not only ease**: slowest move ≈3× the fastest. Our entrances are all 0.38–0.55 s.
4. **Stillness is a move**: not every beat should drift; add "none".
5. **Total stagger ≤ 0.5 s** whatever the word count; order by importance (key word first).
6. **Marker effects on emphasis**: animated underline / circle / highlight sweep drawn on the key word (same draw-on technique as our arrows).
7. **Background depth**: ghost text (chapter name or year, huge, 3–8% opacity, slow drift) gives depth without breaking the white look.
8. **Tighter tracking** on display type (−0.03 to −0.05 em); ours is −0.01.
9. **SFX layer**: ElevenLabs sound generation for whoosh / pop / tick, placed on entrances and count-ups (paid; reference videos had none).
10. **Verification**: extract a frame at every transition midpoint and check for blank frames.
Not applicable: silence/mistake cuts, lower thirds, captions/karaoke, shader transitions (html2canvas limits), audio-reactive (no music), "banned fonts" lists.

## Applied herk-edit-kit tips 1–6 (2026-11-17) → slice v6
1. Lead: visuals start 0.25 s before their word (min 0.3 s after the previous beat); first move ~0.1 s into the beat.
2. Roles by meaning: turn (But/However/Then… → hard cut + jolt, no entrances, still), climax (full date or big figure → 0.6× speed, expo.out, zoom-through, always a marker), closer (last beat of chapter → 1.5×, sine.out, gentle set), hook (first beat after lineup → push-up), normal (seeded, 0.85–1.15×, push-left ~1/6). First version counted every `{big}` as climax (5/23 beats) → limited to dates and big figures (2/23).
3. Speed spread 0.6×–1.5× (+ jitter on normal).
4. "still" drift added; turns are always still.
5. Total stagger ≤ 0.5 s; key word lands first, then the rest.
6. Markers: underline / circle (SVG, pathLength draw-on) and highlight (scaleX sweep), on the first emphasis word. The marked word is wrapped in `.mk-t` so count-up can write into it without deleting the marker. Circle first drawn too large (crossed lines above/below) → tightened, plus side margin on circled words. Highlight at z-index −1 triggered a Hyperframes warning → z-index 0 with the text in a z-index 1 span.
- Check: 0 errors, no extra warnings. Render 48.5 s in ~20 s.
- User approved slice v6 ("Looks good"), 2026-11-17.
- 2026-11-17 feedback: step 1 must ask item count and video length in an AskUserQuestion popup before picking items → SKILL.md step 1, word target per chapter = minutes×170÷items.
- Airlines video: user chose ~15 min for 8 items (~320 words/chapter).

## First full video: "The World's Biggest Airlines Explained In 15 Minutes" (2026-11-17)
- Step 1: popup (item count + length) added to the skill mid-run; user picked 15 min → ~320 words/chapter.
- Step 2: 4 parallel research subagents (2 airlines each) returned sourced facts; script 2,460 words; disputed claims softened.
- Step 3: estimate 1,731 credits for ch1 → 14,084 credits total (~$2.56) for 8 chapters; one call per chapter on one flow; narration 15:44; transcribe 2,437 words (99%).
- Step 4 lessons: (1) Commons non-standard thumbnail widths (2000 px) were throttled for minutes → snap to standard widths (1920/3840), ~3 s per file. (2) No cut-out airline profiles on Commons → new `scripts/cutout.swift` (Vision VNGenerateForegroundInstanceMaskRequest, largest instance, crop) makes lineup PNGs from photos; in-flight shots cut cleanly, ground shots don't; choose right-facing photos (mirroring flips livery text). (3) manifest.json now written under an flock for parallel fetchers.
- Step 5: beats written via a small Python generator (make_beats.py) with shorthands + automatic word check against script.md: 290 beats, words match.

## Airlines video — build and review (2026-11-17)

- Image fetch: 4 parallel fetchers took ~1.5–3.5 h because of Commons 429s. Root cause found by the fetchers:
  when the original is narrower than the asked width, Commons serves the original file, which 429s every
  time and left 0-byte stubs. Fix in `commons.py get`: re-ask at the largest standard width below the
  original, and write via `.part` + rename so a failed fetch leaves no file.
- Gaps: no Commons portrait of Ryanair founder Tony Ryan (the only "Tony Ryan" is a chemist) -> text card.
  Expect a few items with no free photo; a text card is the fallback.
- Review faults fixed in `build.py`:
  - long `{big}` lines overflowed the frame ("THAN WE SHOULD HAVE") -> `text_block` estimates line width
    (Allo Black caps ~0.68 em/char) and shrinks the line with nowrap.
  - circle marker on a long big phrase ("SEPTEMBER 2005") wrapped to 2 lines and ballooned off-frame ->
    circle only on <=8 chars (big) / <=12 chars, else falls back to underline.
- Snapshot gotcha: single `--at` frames sometimes miss a line that a sequence of frames shows; check a
  suspicious frame with several nearby `--at` times before changing code. Frames <0.2 s into a beat are
  blank by design (entrance).

## US F1 video — lineup maps (2026-11-17)

- New lineup kind: circuit maps. Commons has no single style for all 12 US venues (fr.wikipedia's 470 px
  "Circuit X.png/.svg" series covers 9). `commons.py search --drawing` now finds SVG maps.
- `scripts/trackline.swift` redraws any map as one black line of fixed width: dark mask -> fill compact
  marker circles -> opening -> pick the piece with the widest extent (not the most pixels, or a filled
  marker disk wins) -> Zhang-Suen thin -> prune spurs -> dilate. Options --close N / --prune N for maps
  whose turn-number circles cut the line. Larger source drawings (1000+ px) work far better than the
  470 px series. Result is recognisable with small gaps/nubs on 5 maps (Riverside, Watkins, Long Beach,
  Caesars, Miami). ~1.5 h spent; a hand-check per map is still needed.
- Build: `blur_text` after a text card raised 5 `content_overlap` check errors (blurred copy under sharp
  text, by design). Fix in build.py: the `.blurred` layer carries `data-layout-ignore`.
- Image fetch with the commons.py width fix and 3 serial-only fetchers: 79 images in ~15–30 min each
  (airlines took up to 3.5 h). Brief fetchers to run one command at a time.
- 12-item lineup (6x2): zoom fills the frame; map tops touch the top edge on tall maps. Acceptable.

## SpaceX failures video (2026-11-17)

- Lineup agent (fetch + Vision cut-out) ran ~1 h with nothing written to assets; stopped it. Vision
  cut-outs fail on rockets: launch towers, plumes and buildings stay in the mask. New fallback lineup
  style: uniform 3:4 photo cards (ffmpeg scale=600:800:increase,crop=600:800) from beat photos, ideally
  showing the real event. Brief lineup agents with a hard deadline, or do the lineup inline.
- Recent-event topics: Commons often has no ground photo of the exact flight (Starship 7-15). Each
  substitute photo whose caption would name the wrong flight became a text card; captions must never
  claim an event the photo does not show.
