# Design toolkit: motion, colour, type, icons, backgrounds, inspiration

Everything here except the components themselves (those are in [catalog.md](catalog.md)). As with the catalog, confirm package names and APIs on the site's docs before use.

## Motion

Pick one main animation library per project, plus single-purpose helpers where they earn their place. Motion and GSAP both driving the same page is a smell. Before reaching for any of them, check whether native CSS now covers it (View Transitions, `@starting-style` entry animations, scroll-driven animations): ask the modern-web-guidance skill (SKILL.md step 8).

| Library | Use it for | In Next.js |
| --- | --- | --- |
| **Motion** (motion.dev, formerly Framer Motion) | The default. Enter/exit, layout animations, gestures, scroll-linked values, springs. Most component libraries in the catalog already depend on it. | `motion` package, `import { motion } from "motion/react"`, client components only. |
| **GSAP** (gsap.com) | Scroll-driven storytelling, long choreographed timelines, SVG morphing, split-text. GSAP and all its plugins (ScrollTrigger, SplitText, MorphSVG...) are now free. | `gsap` + `@gsap/react` and its `useGSAP` hook (cleans up on unmount). Register plugins once in a client module. |
| **Lenis** (lenis.darkroom.engineering) | Smooth scrolling on marketing and editorial sites; pairs with GSAP ScrollTrigger. Not for app UIs or dashboards. | `lenis`, `ReactLenis` from `lenis/react` in a client provider in the root layout. Turn it off for `prefers-reduced-motion`. |
| **Rive** (rive.app) | Interactive vector animations with state machines (animated mascots, toggles, onboarding, hero illustrations). | `@rive-app/react-canvas`; load the `.riv` from `public/`. |
| **transitions.dev** | Crafted CSS and React transitions (modal, toast, dropdown, tabs, card resize, number pop-in, shimmer text) plus a builder. No install CLI; copy from the builder and adapt to Motion or CSS. | Copy into a client component; convert timings to the project's motion tokens. |
| **LDRS** (uiball.com/ldrs) | Small, tasteful loading spinners. | `ldrs` package (web components with React wrappers); client-only. |

## Colour

Work out the palette before building, then express it as CSS variables / Tailwind v4 `@theme` tokens. Tailwind v4 and current shadcn themes use OKLCH.

- **Realtime Colors** (realtimecolors.com): try text / background / primary / secondary / accent on a live page, then export CSS variables or a Tailwind config. Good first stop for a brand palette.
- **OKLCH** (oklch.com): pick and tweak OKLCH values, check gamut.
- **UI Colors** (uicolors.app) and **tints.dev**: turn one brand hex into a full Tailwind 50-950 scale (tints.dev exports OKLCH).
- **Huemint** (huemint.com): machine-generated palettes with colours assigned to roles on a website mockup.
- **Radix Colors** (radix-ui.com/colors): 12-step scales with defined jobs per step (backgrounds 1-2, components 3-5, borders 6-8, solids 9-10, text 11-12) and matching dark scales. Use when the project needs accessible, systematic neutrals and accents.

Always check text contrast (WCAG AA) for every foreground/background pair, in light and dark.

## shadcn themes and blocks

- **tweakcn** (tweakcn.com): visual editor for shadcn themes (colours, radius, fonts, shadows) with Tailwind v4 output. Apply a theme via its shadcn registry URL or paste the CSS variables into the global CSS.
- **shadcnblocks** (shadcnblocks.com): ready sections (hero, features, pricing, footer...) built on shadcn; installable via the shadcn CLI. Free and paid blocks; paid ones need the user's licence.

## Fonts and type

- **Google Fonts** (fonts.google.com): load with `next/font/google` (self-hosted at build, no layout shift).
- **Fontshare** (fontshare.com): free display and text faces (Satoshi, General Sans, Clash Display, Cabinet Grotesk...). Use with `next/font/local` from `.woff2` files in the project; ask the user before downloading font files.
- **Typescale** (typescale.com): pick a modular scale (for example 1.25 or 1.333) and map it to the Tailwind text sizes in `@theme`.

Default to two families at most: one display face for headings and one text face for body (or one family in several weights). Expose them as `--font-*` tokens.

## Icons

The user's rule: **react-icons, never emojis.** Use these sites to choose a set and find icons, then import from the matching react-icons pack:

| Site | react-icons import |
| --- | --- |
| **Lucide** (lucide.dev) | `react-icons/lu`. Most shadcn registry components already import `lucide-react`; those imports can stay. |
| **Phosphor** (phosphoricons.com) | `react-icons/pi` |
| **Hugeicons** (hugeicons.com) | Not in react-icons. Pick an equivalent from another pack, or ask the user before adding `@hugeicons/react`. |
| **Iconify** (iconify.design) | Search across 200k+ icons to find a name, then use the same icon from a react-icons pack where it exists. |

Stick to one icon set per site so stroke weight and style match.

## Backgrounds

- **BG.ibelick** (bg.ibelick.com): copy-paste CSS / Tailwind background snippets (grids, dots, radial glows) with no dependencies. Recolour to the project tokens.
- **Haikei** (haikei.app): generate SVG backgrounds (waves, blobs, layered peaks, low-poly, gradients) in the browser and export SVG. Put the file in `public/` or turn it into a component with SVGR; recolour to tokens.

Prefer these static backgrounds over a WebGL background on pages that already have heavy motion, and use them as the reduced-motion fallback for animated ones.

## Inspiration

Look before designing a new page, and tell the user which references you drew from:

- **Mobbin** (mobbin.com): real app and web screens by flow (onboarding, pricing, settings). Needs an account; ask the user to sign in if it is gated.
- **Curated** (curated.design): hand-picked modern web design.
- **Landingfolio** (landingfolio.com): landing pages and sections by type.

Take ideas (layout, rhythm, how a section solves its job), not a site's whole look. Do not recreate a specific existing site.
