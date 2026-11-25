# Design toolkit: motion, colour, type, icons, backgrounds, inspiration

Everything here except the components themselves (those are in [catalog.md](catalog.md)). As with the catalog, confirm package names and APIs on the site's docs before use.

## Motion

Pick one main animation library per project, plus single-purpose helpers where they earn their place. Two general-purpose engines on one page (Motion and GSAP and React Spring) is a smell.

| Library | Use it for | In Next.js |
| --- | --- | --- |
| **Motion** (motion.dev, formerly Framer Motion) | The default. Enter/exit, layout animations, gestures, scroll-linked values, springs. Most component libraries in the catalog already depend on it. | `motion` package, `import { motion } from "motion/react"`, client components only. |
| **GSAP** (gsap.com) | Scroll-driven storytelling, long choreographed timelines, SVG morphing, split-text. GSAP and all its plugins (ScrollTrigger, SplitText, MorphSVG...) are now free. | `gsap` + `@gsap/react` and its `useGSAP` hook (cleans up on unmount). Register plugins once in a client module. |
| **AutoAnimate** (auto-animate.formkit.com) | Zero-config motion for lists and containers: items added, removed, reordered. | `@formkit/auto-animate`, `useAutoAnimate()` ref on the parent. |
| **React Spring** (react-spring.dev) | Physics springs, and animation inside react-three-fiber scenes. Use when the project already has it. | `@react-spring/web` (or `/three`). |
| **Anime.js** (animejs.com) | Lightweight timelines and SVG/stroke animation outside React's tree, staggered grids. | `animejs`, run inside `useEffect` and clean up. |
| **Lenis** (lenis.darkroom.engineering) | Smooth scrolling on marketing and editorial sites; pairs with GSAP ScrollTrigger. Not for app UIs or dashboards. | `lenis`, `ReactLenis` from `lenis/react` in a client provider in the root layout. Turn it off for `prefers-reduced-motion`. |
| **Rive** (rive.app) | Interactive vector animations with state machines (animated mascots, toggles, onboarding). | `@rive-app/react-canvas`; load the `.riv` from `public/`. |
| **LottieFiles** (lottiefiles.com) | Ready-made illustrative animations (Lottie / dotLottie). | `@lottiefiles/dotlottie-react`; prefer `.lottie` files, lazy-load below the fold. Check each animation's licence. |
| **LDRS** (uiball.com/ldrs) | Small, tasteful loading spinners. | `ldrs` package (web components with React wrappers); client-only. |
| **Unicorn Studio** (unicorn.studio) | No-code WebGL scenes for a hero background. The user designs the scene there and shares the project ID or embed. | Embed per its docs in a client component loaded with `next/dynamic`, `ssr: false`, with a static image fallback. Check the plan for branding requirements. |

## Colour

Work out the palette before building, then express it as CSS variables / Tailwind v4 `@theme` tokens. Tailwind v4 and current shadcn themes use OKLCH.

- **Realtime Colors** (realtimecolors.com): try text / background / primary / secondary / accent on a live page, then export CSS variables or a Tailwind config. Good first stop for a brand palette.
- **UI Colors** (uicolors.app) and **tints.dev**: turn one brand hex into a full Tailwind 50-950 scale (tints.dev exports OKLCH).
- **Coolors** (coolors.co), **Huemint** (huemint.com), **Color Hunt** (colorhunt.co): generate or browse palettes. Huemint assigns colours to roles for a website mockup.
- **Happy Hues** (happyhues.co) and **Palette Maker** (palettemaker.com): see a palette applied to real UI with roles (background, headline, button) already chosen.
- **OKLCH** (oklch.com): pick and tweak OKLCH values, check gamut.
- **Radix Colors** (radix-ui.com/colors): 12-step scales with defined jobs per step (backgrounds 1-2, components 3-5, borders 6-8, solids 9-10, text 11-12) and matching dark scales. Use when the project needs accessible, systematic neutrals and accents.

Always check text contrast (WCAG AA) for every foreground/background pair, in light and dark.

## shadcn themes and blocks

- **tweakcn** (tweakcn.com): visual editor for shadcn themes (colours, radius, fonts, shadows) with Tailwind v4 output. Apply a theme via its shadcn registry URL or paste the CSS variables into the global CSS.
- **jln themes** (ui.jln.dev): browse and generate thousands of shadcn themes; copy the CSS variables.
- **shadcnblocks** (shadcnblocks.com): ready sections (hero, features, pricing, footer...) built on shadcn; installable via the shadcn CLI. Free and paid blocks.
- **shadcndesign** (shadcndesign.com): premium shadcn blocks and Figma kit; licence needed.

Paid blocks need the user's licence; ask before using them.

## Fonts and type

- **Google Fonts** (fonts.google.com): load with `next/font/google` (self-hosted at build, no layout shift).
- **Fontshare** (fontshare.com): free display and text faces (Satoshi, General Sans, Clash Display, Cabinet Grotesk...). Use with `next/font/local` from `.woff2` files in the project; ask the user before downloading font files.
- **Fontpair** (fontpair.co): heading/body pairing ideas.
- **Typescale** (typescale.com): pick a modular scale (for example 1.25 or 1.333) and map it to the Tailwind text sizes in `@theme`.

Default to two families at most: one display face for headings and one text face for body (or one family in several weights). Expose them as `--font-*` tokens.

## Icons

The user's rule: **react-icons, never emojis.** Use these sites to choose a set and find icons, then import from the matching react-icons pack:

| Site | react-icons import |
| --- | --- |
| **Phosphor** (phosphoricons.com) | `react-icons/pi` |
| **Heroicons** (heroicons.com) | `react-icons/hi2` |
| **Tabler** (tabler.io/icons) | `react-icons/tb` |
| **Hugeicons** (hugeicons.com) | Not in react-icons. Pick an equivalent from another pack, or ask the user before adding `@hugeicons/react`. |
| **Iconify** (iconify.design) | Search across 200k+ icons to find a name, then use the same icon from a react-icons pack where it exists. |

Stick to one icon set per site so stroke weight and style match.

## Backgrounds and patterns

- **Hero Patterns** (heropatterns.com): repeatable SVG patterns as a CSS `background-image`; recolour to the project tokens, keep the opacity low.
- **SVG Backgrounds** (svgbackgrounds.com): SVG backgrounds, some free, some paid; check the licence and attribution terms.

Prefer these static patterns over a WebGL background on pages that already have heavy motion, or as the reduced-motion fallback.

## Inspiration

Look before designing a new page, and tell the user which references you drew from:

- **Mobbin** (mobbin.com): real app and web screens by flow (onboarding, pricing, settings). Needs an account; ask the user to sign in if it is gated.
- **Landingfolio** (landingfolio.com): landing pages and sections by type.
- **Awwwards** (awwwards.com): award-level, motion-heavy sites; good for hero and scroll ideas.
- **Curated** (curated.design): hand-picked modern web design.

Take ideas (layout, rhythm, how a section solves its job), not a site's whole look. Do not recreate a specific existing site.
