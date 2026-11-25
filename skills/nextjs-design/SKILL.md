---
name: nextjs-design
description: Design and build Next.js sites and pages from the user's preferred references - component libraries (React Bits, Aceternity UI, Magic UI, 21st.dev, Origin UI, shadcn-registry animation kits, DaisyUI, HeroUI, headless primitives), motion libraries (Motion, GSAP, Lenis, Rive, Lottie), palette, shadcn theme, font, icon and inspiration sites - instead of hand-rolling everything. Use whenever the user asks to design, build, redesign, restyle or polish a website, landing page, marketing page, dashboard or UI in Next.js or React, pick colours, fonts or icons, add animation, or asks for a hero, navbar, pricing, testimonials, animated background, text effect, drawer, toast or other section, even if no library is named.
---

# Next.js design from reference libraries

When designing anything in Next.js, reach for the user's references first, where they fit:

- [references/catalog.md](references/catalog.md): component libraries (UI kits, animated components, primitives).
- [references/toolkit.md](references/toolkit.md): motion libraries, colour palette tools, shadcn themes and blocks, fonts and type scales, icons, background patterns and inspiration sites.

Hand-write a component only when nothing there fits or the fit would cost more than it gives. Read both files before planning a page.

"Where it fits" matters more than "use as many as possible". A good page uses a few striking pieces on a calm base, not a different effect in every section.

## Workflow

1. **Read the project first.** Check `package.json` (Next.js, React, Tailwind version, `motion` / `framer-motion`, `gsap`, existing UI kits), `components.json` (shadcn set up? which style, base library, registries), the global CSS (Tailwind v4 `@theme` tokens or a v3 config) and existing components. Fit what is there; do not add a second design system to a project that has one.

2. **Set the direction (new sites and redesigns).** Before any component, settle the look with the toolkit: glance at the inspiration sites for how similar pages solve their sections; choose a palette (Realtime Colors, tints.dev / UI Colors for scales, Radix Colors for systematic neutrals) and express it as OKLCH tokens; choose one or two fonts (Google Fonts or Fontshare, paired with Fontpair) and a type scale (Typescale); choose one icon set; for shadcn projects, start from a tweakcn or jln theme instead of the default. Show the user the direction in a few lines (palette, fonts, references) before building. Skip this for a small change to an existing site: use its tokens.

3. **Pick one base layer.** Every page needs one foundation for buttons, inputs, dialogs, menus and theming:
   - Default: **shadcn/ui** (on Radix or Base UI) with Tailwind v4. Almost every animated library in the catalog is a shadcn registry or copy-paste Tailwind code, so this combines with the most.
   - Use **HeroUI**, **DaisyUI**, **Flowbite**, **Mantine** or **Park UI** as the base only when the project already uses it or the user asks. These are full themed systems; never run two of them in one app.
   - Headless primitives (**Radix**, **Base UI**, **Ark UI**, **React Aria**) are for building a custom component when no styled one fits.

4. **Plan the page, then map sections to components.** Write a short section list (hero, logos, features, pricing, FAQ, footer...) and for each pick a component from the catalog's "Pick by need" table, or say "base layer only". Aim for one or two hero-level effects per page (an animated background, a text reveal) and quieter motion elsewhere (fade-ins, hover states, number tickers). Tell the user the plan in a few lines before building a full page.

5. **Get the current component from its source.** Do not write a library's component from memory. Open the component's page on the library site (or its registry JSON) and use its current install command and code. APIs, names and registry URLs change. If the site blocks fetching, try its GitHub repo or registry JSON, or tell the user which component you meant and ask them to paste it.

6. **Install the cleanest way the library offers.**
   - shadcn registry: `npx shadcn@latest add <registry-item>` (namespaced `@magicui/x` style needs the registry in `components.json`; a full `https://.../r/x.json` URL works without it). Check that the command added the dependencies; some registries (Fancy Components) do not.
   - npm package (HeroUI, Mantine, Flowbite React, Vaul, Sonner, primitives): install with the project's package manager.
   - Copy-paste (Uiverse, HyperUI, Lukacho, Origin UI, Tailwind Plus): put the code in `components/` and convert it to TSX with typed props.
   Never overwrite an existing `components/ui/*` file without checking the diff.

7. **Make it belong to the project.**
   - Replace the library's hardcoded colors, fonts and radii with the project's tokens (CSS variables / Tailwind theme). Five libraries' default palettes on one page is the main thing that makes these sites look stitched together.
   - Replace demo copy and images with the real content.
   - Icons: use **react-icons**, never emojis, from the one set chosen in step 2 (Phosphor `pi`, Heroicons `hi2`, Tabler `tb`; see the toolkit). Lucide imports that came with a registry component can stay, but icons you add are react-icons.

8. **Next.js rules.**
   - Anything using hooks, `motion`, GSAP, canvas or `window` needs `"use client"`. Keep pages and layouts server components; wrap the animated piece in a small client component instead of marking the whole page.
   - Heavy WebGL/canvas pieces (three, ogl, cobe globes, particle and shader backgrounds) load with `next/dynamic` and `ssr: false`, and render a static fallback.
   - `motion` imports from `motion/react` (older code uses `framer-motion`; do not install both unless something requires it).
   - One main animation engine per project: Motion by default, GSAP (with `useGSAP`) for scroll-driven timelines. Add helpers (AutoAnimate, Lenis, Rive, Lottie, LDRS) only for their specific job; see the toolkit's Motion table.
   - Use `next/image` and `next/font` in place of raw `<img>` and font `<link>` tags in pasted code.

9. **Motion and accessibility.** Respect `prefers-reduced-motion` (Motion's `useReducedMotion` or a `motion-safe:` / `motion-reduce:` variant), keep text readable while it animates, keep contrast at WCAG AA over animated backgrounds, and keep every interactive effect reachable by keyboard. Prefer accessible bases (Radix, Base UI, React Aria) for anything interactive; a Uiverse button styled from a `<div>` becomes a real `<button>`.

10. **Check it.** Run the build and the dev server, open the page, and look at it at desktop and phone widths in light and dark if the site has both. Check for hydration warnings, layout shift from late-loading effects, and frame drops from stacked animations. Report what you checked.

## Licences

Most of these libraries are MIT or free. Paid parts are not: **Tailwind Plus** (formerly Tailwind UI), shadcndesign, and paid shadcnblocks and SVG Backgrounds items need the user's licence, and Aceternity, Magic UI and several others have Pro tiers. Use paid components only when the user confirms they have access. Note each library's licence in the summary when it requires attribution.

## Keeping the list current

The user's references are in [references/catalog.md](references/catalog.md) (components) and [references/toolkit.md](references/toolkit.md) (motion, colour, themes, fonts, icons, backgrounds, inspiration). When they name a new one to add, add it to the right file and group with how to use it in Next.js and what it is best for, and push the change to their skills repo (`byalex33/skills`, `skills/nextjs-design/`).
