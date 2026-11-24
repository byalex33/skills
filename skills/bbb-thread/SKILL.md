---
name: bbb-thread
description: Make the BuiltByBit listing assets for a product (the long thread design image, the 2:1 cover, the update title and BBCode notes, and the BBCode text version) as HTML rendered to PNG with headless Chrome, in the Mint tweakcn theme, with real screenshots of the product. Use when the user asks for a thread design, a resource cover, update notes or a listing description for BuiltByBit, or to refresh them after new features.
---

# BuiltByBit thread assets

Every asset is an HTML page rendered to PNG by the user's installed Google Chrome through `playwright-core`. Work outside Figma: read a Figma link only to see the old layout, and never write to it. The thread uses the **Mint** theme ([`MINT.md`](MINT.md)); screenshots of the product show the product in its **own default theme**, untouched.

Accuracy is the bar for every word: each feature claim, number and tech name is checked against the code, `package.json` or the product's docs, never copied forward from old listing text.

## 1. Gather

- The feature list, from the code, `README`, recent commits and the version in `package.json`. Mark what is new since the last listing.
- The old layout, if there is one: a Figma frame (`get_screenshot` of the frame, then of each child section, since one tall screenshot loses detail), or the current thread image on BuiltByBit (read it in the built-in browser; the feature list there is usually inside an image).

Done when you can name every section of the old design and every feature, each marked new or existing.

## 2. Screenshots

1. The scripts in `scripts/` load `playwright-core` from their own folder, which drives `/Applications/Google Chrome.app` (no browser download). If `scripts/node_modules` is missing, run `npm install` in `scripts/`. Put the capture script in a scratch folder with its own `npm i playwright-core`.
2. Back up the product's local data file (for example `.data/*.json`) before anything writes to it. Seed demo data if charts look empty or show steep drops (a project seed script, if one exists).
3. Start the product's dev server with `preview_start`. Next.js allows one dev server per folder: if another Claude session shares the folder, agree a slot with it by `SendMessage` and stop only processes you started.
4. Write a capture script modelled on [`examples/pastify/capture.mjs`](examples/pastify/capture.mjs): viewport 1280 × 800 at 2×, dark scheme, the Next.js dev badge hidden (`nextjs-portal{display:none}`), toasts waited out before each shot, admin login read from the project's own `.env.local`.
5. Read every shot. Retake any with a toast, a dev badge, `localhost` text, stale cached settings or an empty state.
6. Restore the data file from the backup and stop the server.

Done when each showcase has a clean shot and the data file matches the backup.

## 3. Thread design

Build `thread.html` at 1920 px wide, following [`examples/pastify/thread.html`](examples/pastify/thread.html): hero (logo, version badge, headline, lead, two buttons, product shot), feature grid with a mint `NEW` tag on new cards, alternating screen showcases with check lists, tech chips, CTA card. Browser bars read `paste.example.com`-style addresses. A showcase whose screenshot would leak `localhost` or test data becomes an HTML code card instead.

Render with `node <skill>/scripts/render.mjs thread.html out.png 1920`, then read it with `node <skill>/scripts/slices.mjs thread.html slices/` (half-size 1600 px slices). `<skill>` is this skill's folder. Fix widows, clipped text and empty space, render again.

Done when every slice reads cleanly and every claim on the page passed the accuracy bar.

## 4. Cover

Build `cover.html` at 1024 × 512 (2:1), following [`examples/pastify/cover.html`](examples/pastify/cover.html), and render at 2× with `node <skill>/scripts/render.mjs cover.html cover.png 1024 512 2` for a 2048 × 1024 PNG. Keep text inside the middle so a crop loses nothing.

## 5. Text

- **Update title**: plain text, `vX.Y.Z - <the headline features>`.
- **Update notes**: BBCode, grouped by feature, then a numbered "How to update" with any new dependency or migration step.
- **Text version**: the listing's `[SPOILER="Text version (More Info)"]` block in BBCode, rewritten to match the product today. Before writing, list each claim in the old text that is now false and say so to the user.

BuiltByBit BBCode: `[B]`, `[SIZE=5]`, `[LIST]`/`[LIST=1]` with `[*]`, `[ICODE]`, `[SPOILER="…"]`.

## 6. Deliver

Save the PNGs, the HTML sources, the shots they use and the capture script in a `thread-design/` folder in the project, and send each PNG with `SendUserFile`. Leave the folder uncommitted unless the user asks.
