#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { createServer, type Plugin } from "vite";

const ZERO_UI = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const VIRTUAL_ID = "virtual:manual-fragment";
const PAGE_MARGIN = "18mm";
// A4 is 210 × 297 mm; at the CSS 96 dpi that leaves this much inside the margins.
const PRINTABLE = { width: 658, height: 986 };
const PROSE_WORD_LIMIT = 425;

const manualFragment = (html: string): Plugin => ({
  name: "manual-fragment",
  resolveId: (id) => (id === VIRTUAL_ID ? `\0${VIRTUAL_ID}` : undefined),
  load: (id) => (id === `\0${VIRTUAL_ID}` ? `export default ${JSON.stringify(html)};` : undefined),
});

const escapeHtml = (text: string) =>
  text.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

const footer = (title: string, version: string) => `
  <div style="width: 100%; padding: 0 ${PAGE_MARGIN}; display: flex; justify-content: space-between;
              font-family: Inter, sans-serif; font-size: 8px; color: #6b7280;">
    <span>${escapeHtml(title)}</span>
    <span>${escapeHtml(version)}</span>
    <span><span class="pageNumber"></span> / <span class="totalPages"></span></span>
  </div>`;

const render = async (fragmentPath: string) => {
  const html = await readFile(fragmentPath, "utf8");
  const outputBase = join(dirname(fragmentPath), basename(fragmentPath, ".html"));

  const server = await createServer({
    configFile: join(ZERO_UI, "vite.config.ts"),
    root: ZERO_UI,
    logLevel: "error",
    server: { port: 5290 },
    plugins: [manualFragment(html)],
  });
  await server.listen();
  const browser = await chromium.launch();

  try {
    const page = await browser.newPage({ viewport: PRINTABLE });
    await page.emulateMedia({ media: "print", colorScheme: "light" });
    const pageError = new Promise<never>((_, reject) =>
      page.on("pageerror", (error) =>
        reject(
          new Error("Manual failed to render; the browser error is logged above.", {
            cause: error,
          }),
        ),
      ),
    );
    await page.goto(new URL("scripts/manual-print/index.html", server.resolvedUrls!.local[0]).href);
    await Promise.race([
      page.waitForSelector("body[data-rendered]", { timeout: 30_000 }),
      pageError,
    ]);

    const title = await page.$eval("h1", (h1) => h1.textContent ?? "");
    const version = await page.evaluate(
      () => document.querySelector("p.version")?.textContent?.trim() ?? "",
    );
    const proseWords = await page.$eval("#tuning", (tuning) => {
      const prose = document.createRange();
      prose.setStartBefore(tuning.parentElement!.firstChild!);
      prose.setEndBefore(tuning);
      const fragment = prose.cloneContents();
      fragment.querySelectorAll("figure").forEach((figure) => figure.remove());
      return fragment.textContent!.split(/\s+/).filter(Boolean).length;
    });

    await page.screenshot({ path: `${outputBase}.png`, fullPage: true });
    await page.pdf({
      path: `${outputBase}.pdf`,
      preferCSSPageSize: true,
      printBackground: true,
      displayHeaderFooter: true,
      headerTemplate: "<span></span>",
      footerTemplate: footer(title, version),
    });

    console.log(`Wrote ${outputBase}.pdf and ${outputBase}.png`);
    console.log(
      `Prose above Tuning: ${proseWords} of ${PROSE_WORD_LIMIT} words` +
        (proseWords > PROSE_WORD_LIMIT ? " — too long, cut the prose" : ""),
    );
  } finally {
    await browser.close();
    await server.close();
  }
};

const [fragmentPath] = process.argv.slice(2);
if (!fragmentPath) {
  console.error("Usage: pnpm render-manual <path/to/module.html>");
  process.exit(1);
}
await render(resolve(fragmentPath));
