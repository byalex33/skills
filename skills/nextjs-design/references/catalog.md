# Component library catalog

The user's component libraries for Next.js design. Install commands and component names drift: confirm them on the component's own page before use (see SKILL.md step 5). "shadcn registry" means `npx shadcn@latest add ...` works.

## Pick by need

| Need | First look at | Also good |
| --- | --- | --- |
| Hero background (aurora, beams, grid, particles, shaders) | React Bits Backgrounds, Aceternity | Magic UI, Skiper UI; static: see toolkit Backgrounds |
| Headline / text effect (split, scramble, gradient, typewriter) | React Bits Text Animations, Magic UI | Motion Primitives, Aceternity, Cult UI |
| Bento / feature grid | Magic UI (Bento Grid), Aceternity | 21st.dev, Cult UI |
| Logo cloud, marquee | Magic UI (Marquee) | React Bits |
| Testimonials, cards, 3D tilt / hover cards | Aceternity | Skiper UI, BeUI |
| Stats, number tickers | Magic UI (Number Ticker), Animate UI (Sliding Number) | Motion Primitives |
| Pricing, CTA, footer, navbar, whole marketing sections | 21st.dev | Cult UI, Origin UI; blocks: toolkit shadcnblocks |
| Forms, inputs, date pickers, file upload, steppers | Origin UI (coss.com/origin) | shadcn/ui, HeroUI, Astryx |
| Buttons with personality | Kokonut UI, Magic UI | Cult UI, React Bits |
| Animated versions of standard shadcn parts (tabs, accordion, switch) | Animate UI | Motion Primitives, BeUI |
| AI chat, prompt input, model selector | Kokonut UI | BeUI, 21st.dev |
| Dashboards, charts, KPI cards | Tremor | shadcn charts |
| Unusual scroll, hover and image effects | Skiper UI, BeUI | React Bits, Origin Kit |
| Drawer / bottom sheet | Vaul | shadcn Drawer (built on Vaul) |
| Toasts | Sonner | shadcn Sonner |
| Accessible primitive to build on | Radix, Base UI | React Aria |

## Animated and effect libraries (layer on the base)

**React Bits** (reactbits.dev): animated text, backgrounds and interactive components. shadcn registry, namespaced `@react-bits/<Name>-<JS|TS>-<CSS|TW>`, for example `npx shadcn@latest add @react-bits/SplitText-TS-TW`; pick the TS-TW variant for Tailwind projects. Dependencies vary per component (Motion, GSAP, ogl, three): read the component's Code tab. Best for: hero backgrounds, text reveals, cursor effects.

**Aceternity UI** (ui.aceternity.com): flashy marketing components. shadcn registry; copy the command from the component page. Tailwind + Motion. Best for: hero sections, spotlight and beam backgrounds, 3D cards, timelines, testimonials. Pro tier exists.

**Magic UI** (magicui.design): shadcn-native animated components for landing pages. `npx shadcn@latest add @magicui/<name>`. Tailwind + Motion. Best for: marquee, bento grid, number ticker, animated beam, globe, shimmer button, border beam. Pro templates exist.

**21st.dev**: community registry of React + Tailwind components, sections and themes from many authors. Each component page has its own shadcn install command and a "Copy prompt" for agents. Quality varies by author: read the code before installing. Best for: complete sections (heroes, pricing, CTAs) and finding several takes on one idea.

**Animate UI** (animate-ui.com): animated versions of shadcn-style components on Radix, Base UI or React Aria. CLI `npx @animate-ui/cli@latest`, also shadcn registry items. Best for: tabs, accordion, switch, checkbox, sliding number, animated icons, when the project already uses shadcn and just needs motion.

**Motion Primitives** (motion-primitives.com): Motion-based primitives for React + Tailwind. CLI or shadcn registry; check the docs (the site may block automated fetches, so try its GitHub repo). Best for: text effects, transitions, morphing dialogs, in-view reveals, carousels.

**Kokonut UI** (kokonutui.com): 100+ components, many for AI chat apps. Registry `@kokonutui` at `https://kokonutui.com/r/{name}.json`, for example `npx shadcn@latest add @kokonutui/particle-button`. Tailwind + Motion + shadcn. Best for: AI input and tool-call UIs, hold-to-confirm and slide-to-confirm buttons, command palette.

**Cult UI** (cult-ui.com): shadcn-compatible animated components and blocks. shadcn registry URLs from each component page. Best for: dynamic island, expandable cards, texture buttons, text animations, AI-agent blocks.

**Skiper UI** (skiper-ui.com): large set of experimental animated components, numbered (skiper1, skiper2 ...). shadcn registry; copy the command from the page. Some are paid. Best for: unusual hover, scroll and image effects.

**BeUI** (beui.dev): about 160 React components (plus React Native) built with Motion and Tailwind v4, React 19. shadcn registry `@beui/<name>`, for example `npx shadcn add @beui/bookshelf`. Best for: playful product UI such as dynamic island, before/after slider, arc picker, voice orb, infinite masonry.

**Origin Kit** (originkit.dev): free animated component library for modern websites. The site renders client-side, so open it in the browser to read install steps and the component list.

**Origin UI** (coss.com/origin): copy-paste Tailwind + React components built on Base UI. Best for: the practical parts other kits skip, such as date and event calendars, image cropper, file upload, steppers, trees, timelines, sliders, navbars.

## Full component systems (use as the base, never two at once)

**HeroUI** (heroui.com, formerly NextUI): polished React components with Tailwind theming, built on React Aria. Check the docs for the current major version's setup (it changed between v2 and v3). Best for: app UIs that want a complete, consistent kit fast.

**Astryx** (astryx.atmeta.com): Meta's open-source React design system, in beta. React 19+, styled with StyleX (Tailwind and plain CSS also supported). `npm install @astryxdesign/core @stylexjs/stylex @astryxdesign/theme-neutral @astryxdesign/cli`, then `npx @astryxdesign/cli init`; import its reset and base CSS, wrap the app in its `<Theme>`, and import components per entry (`@astryxdesign/core/Button`). Ships several themes and a CLI for components and templates. Use it as the base when the user wants it; being in beta, pin the version and expect breaking changes. Do not mix it with shadcn/HeroUI on the same components.

**Tremor** (tremor.so): dashboard components and charts (Recharts) for Tailwind, copy-paste. Best for: KPI cards, charts, tables, admin dashboards. Sits alongside a shadcn base without conflict.

## Headless primitives (build your own on these)

**Radix Primitives** (radix-ui.com): accessible unstyled primitives; shadcn/ui's original base.

**Base UI** (base-ui.com): unstyled accessible components from the Radix, Floating UI and MUI teams; an alternative base for shadcn/ui, and the base of Origin UI.

**React Aria** (react-spectrum.adobe.com/react-aria): Adobe's accessibility-first hooks and components with strong i18n and keyboard behaviour. Base of HeroUI. Pick it for complex widgets (date pickers, comboboxes, grids) where accessibility must be right.

## Single-purpose (Emil Kowalski)

**Vaul** (vaul.emilkowal.ski): drawer / bottom sheet for React. The shadcn Drawer wraps it. Check the repo for its maintenance status before adding it fresh.

**Sonner** (sonner.emilkowal.ski): toast notifications. `npm i sonner`, mount `<Toaster />` once in the root layout, call `toast()`. The shadcn Sonner component wraps it.
