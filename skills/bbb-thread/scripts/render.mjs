// Renders an HTML file to PNG with the installed Google Chrome.
//   node render.mjs <page.html> <out.png> <width> [height] [scale]
// With no height the shot is the full page (the thread); with a height it is
// exactly that size (the cover). Node resolves `playwright-core` from this
// script's folder: run `npm install` here once.
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const [html, out, width = "1920", height, scale = "1"] = process.argv.slice(2);
if (!html || !out) {
  console.error("Usage: node render.mjs <page.html> <out.png> <width> [height] [scale]");
  process.exit(1);
}
const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({
  viewport: { width: Number(width), height: Number(height ?? 1080) },
  deviceScaleFactor: Number(scale),
});
await page.goto(pathToFileURL(html).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(500);
await page.screenshot({ path: out, fullPage: !height });
const size = await page.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.scrollHeight]);
const icons = await page.evaluate(() => document.querySelectorAll("i[data-lucide]").length);
console.log(`page ${size[0]} x ${size[1]} css px, scale ${scale}${icons ? `, ${icons} icons did not render` : ""}`);
await browser.close();
