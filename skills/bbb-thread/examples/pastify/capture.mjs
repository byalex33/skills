// Takes product screenshots of the local dev site for the thread design.
// Usage: node capture.mjs <baseUrl> <outDir> <envFile>
import { readFileSync } from "node:fs";
import { chromium } from "playwright-core";

const [base, out, envFile] = process.argv.slice(2);
const env = Object.fromEntries(
  readFileSync(envFile, "utf8").split("\n").filter((l) => /^[A-Z_]+=/.test(l)).map((l) => [l.slice(0, l.indexOf("=")), l.slice(l.indexOf("=") + 1)]),
);
const browser = await chromium.launch({ executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless: true });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 2, colorScheme: "dark" });
// Hide the Next.js dev badge in every shot.
await ctx.addInitScript(() => {
  const style = () => {
    const el = document.createElement("style");
    el.textContent = "nextjs-portal{display:none!important}";
    document.documentElement.appendChild(el);
  };
  if (document.documentElement) style();
  else document.addEventListener("DOMContentLoaded", style);
});
const page = await ctx.newPage();
const settle = () => page.waitForTimeout(900);

const CODE = `import { createServer } from "node:http";

type Paste = { id: string; code: string; language: string };

const pastes = new Map<string, Paste>();

export function savePaste(code: string, language = "auto"): Paste {
  const id = crypto.randomUUID().slice(0, 8);
  const paste = { id, code, language };
  pastes.set(id, paste);
  return paste;
}

createServer((req, res) => {
  const id = req.url?.slice(1) ?? "";
  const paste = pastes.get(id);
  if (!paste) {
    res.writeHead(404).end("Not found");
    return;
  }
  res.writeHead(200, { "content-type": "text/plain" });
  res.end(paste.code);
}).listen(3000);
`;

// Admin first: turn the API on, so the docs and settings look live.
await page.goto(`${base}/admin`);
await page.fill('input[name="username"]', env.ADMIN_USERNAME || "admin");
await page.fill('input[name="password"]', env.ADMIN_PASSWORD);
await page.click('button[type="submit"]');
await page.waitForSelector("text=Last 7 days");
// Shots show the app's own default theme.
await page.goto(`${base}/admin#appearance`);
await settle();
const useDefault = page.locator("button", { hasText: /^Use default$/ });
if (await useDefault.count()) {
  await useDefault.click();
  await page.waitForTimeout(2000);
}
await page.goto(`${base}/admin#limits`);
await settle();
const api = page.locator('[role="switch"]').first();
if ((await api.getAttribute("aria-checked")) !== "true") {
  await api.click();
  await page.locator('button[type="submit"]', { hasText: "Save" }).click();
  await page.waitForTimeout(1500);
}
await page.screenshot({ path: `${out}/admin-limits.png` });
await page.goto(`${base}/admin#overview`);
await page.reload();
await page.waitForSelector("text=All time");
await page.waitForTimeout(2500); // charts animate in
await page.screenshot({ path: `${out}/admin-overview.png` });
await page.goto(`${base}/admin#advanced`);
await settle();
await page.screenshot({ path: `${out}/admin-advanced.png` });
await page.goto(`${base}/admin#discord`);
await settle();
await page.screenshot({ path: `${out}/admin-discord.png` });
await page.goto(`${base}/admin#appearance`);
await settle();
await page.screenshot({ path: `${out}/admin-appearance.png` });

// Editor with code, then the Clean up menu open.
await page.goto(`${base}/`);
await page.evaluate(() => localStorage.removeItem("pastify-draft"));
await page.reload();
await page.fill('textarea[aria-label="Code"]', CODE);
await page.waitForTimeout(800);
await page.click("body", { position: { x: 5, y: 790 } });
await page.screenshot({ path: `${out}/editor.png` });
await page.locator("button", { hasText: "Clean up" }).click();
await page.waitForTimeout(400);
await page.screenshot({ path: `${out}/editor-cleanup.png` });
await page.keyboard.press("Escape");

// Save it and shoot the paste view.
await page.locator("button", { hasText: /^Save$/ }).click();
await page.waitForURL(/\/view\//);
// Let the "Paste saved" toast leave.
await page.waitForTimeout(7000);
await page.mouse.move(0, 0);
await page.screenshot({ path: `${out}/view.png` });

// API docs.
await page.goto(`${base}/docs`);
await settle();
await page.screenshot({ path: `${out}/docs.png` });

await browser.close();
console.log("done");
