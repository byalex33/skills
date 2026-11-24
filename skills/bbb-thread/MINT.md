# Mint theme for thread assets

The user's Mint theme on tweakcn: <https://tweakcn.com/themes/cmwfrzbat000004jqgblp73v5> (registry JSON at `https://tweakcn.com/r/themes/cmwfrzbat000004jqgblp73v5`). Thread assets use the **dark** tokens below. If the registry has changed, the registry wins: fetch it and update this file.

```css
:root {
  --background: oklch(0 0 0);
  --foreground: oklch(0.9551 0 0);
  --card: oklch(0.1448 0 0);
  --popover: oklch(0.2210 0.0015 197.0452);
  --primary: oklch(0.8545 0.1675 159.6564);   /* mint */
  --primary-foreground: oklch(0 0 0);
  --secondary: oklch(0.4700 0.0900 160.0079);
  --muted: oklch(0.2653 0.0037 286.1465);
  --muted-foreground: oklch(0.6731 0 0);
  --accent: oklch(0.3004 0.0609 159.8938);    /* dark mint, icon tiles on NEW cards */
  --border: oklch(0.2138 0.0019 286.2347);
  --input: oklch(0.3523 0 0);
  --destructive: oklch(0.7425 0.1696 1.0847);
  --chart-2: oklch(0.9173 0.1562 144.8458);
  --chart-4: oklch(0.8104 0.1216 228.4326);   /* code strings */
  --chart-5: oklch(0.8257 0.1067 48.5116);    /* code numbers */
  --radius: 1.4rem;
}
```

- **Fonts**: Outfit (sans, 400 to 800) and IBM Plex Mono (mono), from Google Fonts.
- **Glow**: `radial-gradient(closest-side, oklch(0.8545 0.1675 159.6564 / 0.30), transparent)` behind the hero shot, the screens and the CTA logo.
- **Primary button**: mint fill, black text, a soft mint `box-shadow` glow.
- **Eyebrows**: IBM Plex Mono, uppercase, `letter-spacing: 0.22em`, mint.
- **Headings**: weight 700 to 800, tight tracking (`-0.035em` to `-0.055em`), `text-wrap: balance`.
- **Icons**: Lucide from `https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js`, `<i data-lucide="name">` then `lucide.createIcons()`.
