---
name: nextjs-design
description: Design and build Next.js sites and pages from the user's preferred references - component libraries (React Bits, Aceternity UI, Magic UI, 21st.dev, Animate UI, Kokonut UI, Origin UI, HeroUI, Astryx, headless primitives), motion libraries (Motion, GSAP, Lenis, Rive), palette, shadcn theme, font, icon, background and inspiration sites - together with the modern-web-guidance and unslop skills, instead of hand-rolling everything. Use whenever the user asks to design, build, redesign, restyle or polish a website, landing page, marketing page, dashboard or UI in Next.js or React, pick colours, fonts or icons, add animation, or asks for a hero, navbar, pricing, testimonials, animated background, text effect, drawer, toast or other section, even if no library is named.
---

# Next.js design from reference libraries

When designing anything in Next.js, reach for the user's references first, where they fit:

- [references/catalog.md](references/catalog.md): component libraries (animated kits, full systems, primitives).
- [references/toolkit.md](references/toolkit.md): motion libraries, colour palette tools, shadcn themes and blocks, fonts and type scales, icons, backgrounds and inspiration sites.

Hand-write a component only when nothing there fits or the fit would cost more than it gives. Read both files before planning a page.

"Where it fits" matters more than "use as many as possible". A good page uses a few striking pieces on a calm base, not a different effect in every section.

## Companion skills

This skill works with two others. Use both on every design task.

- **modern-web-guidance** (GoogleChrome/modern-web-guidance): current web-platform best practice and browser support, so code uses native features (View Transitions, `@starting-style`, scroll-driven animations, container queries, `oklch`, `text-wrap: balance`, popover / dialog) instead of legacy patterns or extra JS. Use it in steps 8 and 10.
- **unslop** (heydamir/unslop): turns AI-looking UI into a designed interface: direction from the product, then spacing, colour, icons, copy, type, layout, details, visuals and motion passes, and an audit of the usual tells (purple gradients, glows, gradient text, emoji labels, pulsing elements, uneven spacing). Use it in steps 2 and 10. When the user asks to polish or "unslop" an existing screen, run unslop as the main process and use this skill's references for any components it calls for.

**If either is not installed** (it is not in the available skills list), install it before starting:

```
claude plugin marketplace add GoogleChrome/modern-web-guidance
claude plugin install modern-web-guidance@googlechrome
claude plugin marketplace add heydamir/unslop
claude plugin install unslop@heydamir
```

A newly installed plugin's skill may only load in a new session. Until then, read the skill's `SKILL.md` from the installed plugin folder (`~/.claude/plugins/`) or from GitHub and follow it. modern-web-guidance also works without installing, through its CLI: `npx modern-web-guidance@latest search "<task>"`, `retrieve "<guide-id>"` and `legacy-scan .` (Node 22+).

## Workflow

1. **Read the project first.** Check `package.json` (Next.js, React, Tailwind version, `motion` / `framer-motion`, `gsap`, existing UI kits), `components.json` (shadcn set up? which style, base library, registries), the global CSS (Tailwind v4 `@theme` tokens or a v3 config) and existing components. Fit what is there; do not add a second design system to a project that has one.

2. **Set the direction (new sites and redesigns).** Write unslop's five direction lines (product, character, world, moments, signature), derived from what the product is, not from trends. Then make them concrete with the toolkit: glance at the inspiration sites for how similar pages solve their sections; choose a palette (Realtime Colors and OKLCH to explore, tints.dev / UI Colors for scales, Radix Colors for systematic neutrals) and express it as OKLCH tokens; choose one or two fonts (Google Fonts or Fontshare) and a type scale (Typescale); choose one icon set; for shadcn projects, start from a tweakcn theme instead of the default. Show the user the direction in a few lines before building. Skip this for a small change to an existing site: use its tokens.

3. **Pick one base layer.** Every page needs one foundation for buttons, inputs, dialogs, menus and theming:
   - Default: **shadcn/ui** (on Radix or Base UI) with Tailwind v4. Almost every animated library in the catalog is a shadcn registry or copy-paste Tailwind code, so this combines with the most.
   - Use **HeroUI** or **Astryx** as the base only when the project already uses it or the user asks. They are full themed systems; never run two in one app.
   - Headless primitives (**Radix**, **Base UI**, **React Aria**) are for building a custom component when no styled one fits.

4. **Plan the page, then map sections to components.** Write a short section list (hero, logos, features, pricing, FAQ, footer...) and for each pick a component from the catalog's "Pick by need" table, or say "base layer only". Put the richness in the one or two "moments" from the direction (an animated background, a text reveal, a rich chart) and keep the chrome quiet, with gentler motion elsewhere (fade-ins, hover states, number tickers). Tell the user the plan in a few lines before building a full page.

5. **Get the current component from its source.** Do not write a library's component from memory. Open the component's page on the library site (or its registry JSON) and use its current install command and code. APIs, names and registry URLs change. If the site blocks fetching, try its GitHub repo or registry JSON, or tell the user which component you meant and ask them to paste it.

6. **Install the cleanest way the library offers.**
   - shadcn registry: `npx shadcn@latest add <registry-item>` (namespaced `@magicui/x` style needs the registry in `components.json`; a full `https://.../r/x.json` URL works without it). Check that the command added the dependencies.
   - npm package (HeroUI, Astryx, Vaul, Sonner, primitives): install with the project's package manager.
   - Copy-paste (Origin UI, transitions.dev, BG.ibelick, Tremor): put the code in `components/` and convert it to TSX with typed props.
   Never overwrite an existing `components/ui/*` file without checking the diff.

7. **Make it belong to the project.**
   - Replace the library's hardcoded colors, fonts and radii with the project's tokens (CSS variables / Tailwind theme). Five libraries' default palettes on one page is the main thing that makes these sites look stitched together.
   - Replace demo copy and images with the real content.
   - Icons: use **react-icons**, never emojis, from the one set chosen in step 2 (Lucide `lu`, Phosphor `pi`; see the toolkit). `lucide-react` imports that came with a registry component can stay.

8. **Next.js and platform rules.**
   - Before writing CSS or browser-API code for layout, animation, dialogs, popovers, forms or scrolling, search modern-web-guidance for the task and follow it. Prefer the native feature when it covers the job; add a JS library only for what the platform cannot do.
   - Anything using hooks, `motion`, GSAP, canvas or `window` needs `"use client"`. Keep pages and layouts server components; wrap the animated piece in a small client component instead of marking the whole page.
   - Heavy WebGL/canvas pieces (three, ogl, cobe globes, particle and shader backgrounds) load with `next/dynamic` and `ssr: false`, and render a static fallback (a BG.ibelick or Haikei background).
   - `motion` imports from `motion/react` (older code uses `framer-motion`; do not install both unless something requires it).
   - One main animation engine per project: Motion by default, GSAP (with `useGSAP`) for scroll-driven timelines. Add helpers (Lenis, Rive, LDRS) only for their specific job; see the toolkit's Motion table.
   - Use `next/image` and `next/font` in place of raw `<img>` and font `<link>` tags in pasted code.

9. **Motion and accessibility.** Respect `prefers-reduced-motion` (Motion's `useReducedMotion` or a `motion-safe:` / `motion-reduce:` variant), keep text readable while it animates, keep contrast at WCAG AA over animated backgrounds, and keep every interactive effect reachable by keyboard. Prefer accessible bases (Radix, Base UI, React Aria) for anything interactive.

10. **Check it.**
    - Run the build and the dev server, open the page, and look at it at desktop and phone widths in light and dark if the site has both. Check for hydration warnings, layout shift from late-loading effects, and frame drops from stacked animations.
    - Run unslop's audit (its `references/signs.md`) on the rendered page and fix every sign it finds. Library effects are not exempt: a glow, gradient headline or pulsing badge from a component kit counts as slop unless it is one of the chosen moments.
    - Run `npx modern-web-guidance@latest legacy-scan .` on the files you changed and modernise what it flags, when it applies.
    - Report what you checked.

## Licences

Most of these libraries are MIT or free. Paid parts are not: paid shadcnblocks blocks and Pro tiers of Aceternity, Magic UI, Skiper UI and others need the user's licence. Use paid components only when the user confirms they have access. unslop is CC BY 4.0: keep its credit if any of its text is copied into the project. Note each library's licence in the summary when it requires attribution.

## Keeping the list current

The user's references are in [references/catalog.md](references/catalog.md) (components) and [references/toolkit.md](references/toolkit.md) (motion, colour, themes, fonts, icons, backgrounds, inspiration). When they name a new one to add, add it to the right file and group with how to use it in Next.js and what it is best for; when they give a full new list, replace the old one so removed entries go too. Push the change to their skills repo (`byalex33/skills`, `skills/nextjs-design/`).
