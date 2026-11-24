// Renders a tall page as half-size slices, 1600 css px each, for reading.
//   node slices.mjs <page.html> <outDir> [width]
import { mkdirSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const [html, outDir, width = "1920"] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: Number(width), height: 1080 }, deviceScaleFactor: 0.5 });
await page.goto(pathToFileURL(html).href, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
const h = await page.evaluate(() => document.documentElement.scrollHeight);
let i = 0;
for (let y = 0; y < h; y += 1600, i++) {
  await page.screenshot({
    path: `${outDir}/slice${i}.png`,
    fullPage: true,
    clip: { x: 0, y, width: Number(width), height: Math.min(1600, h - y) },
  });
}
console.log(`${i} slices in ${outDir}`);
await browser.close();
