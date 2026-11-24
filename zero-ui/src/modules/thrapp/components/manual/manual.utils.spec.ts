import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import { describe, expect, it } from "vitest";
import {
  checkManual,
  linkParameters,
  outlineManual,
  paintModeBadges,
  parameterField,
  readManualStamp,
} from "./manual.utils";

describe("paintModeBadges", () => {
  it("colors each mode badge like the mimic ModeBadge", () => {
    const root = document.createElement("article");
    root.innerHTML = `<span data-mode="Filling">filling</span><span data-mode="Unknown">x</span>`;

    paintModeBadges(root);

    const [filling, unknown] = root.querySelectorAll<HTMLElement>("[data-mode]");
    expect(filling.style.backgroundColor).toBe(MODE_COLORS[ModeBadgeMode.Filling]);
    expect(unknown.style.backgroundColor).toBe("");
  });
});

describe("readManualStamp", () => {
  it("reads the control version and issue date the manual was stamped with", () => {
    const html = `<h1>PVT</h1>
<p
  class="version"
  data-module="pvt"
  data-facts="1e42533"
>
  Control version 1e42533 · 2026-11-04
</p>`;

    expect(readManualStamp(html)).toEqual({ version: "1e42533", issued: "2026-11-04" });
  });

  it("is undefined for a manual that was never stamped", () => {
    expect(readManualStamp("<h1>PVT</h1>")).toBeUndefined();
  });
});

describe("outlineManual", () => {
  it("lists the sections, giving each heading an id to link to", () => {
    const root = document.createElement("article");
    root.innerHTML = `<h2>What it does</h2><h3>Not a section</h3><h2 id="tuning">Tuning</h2>`;

    expect(outlineManual(root)).toEqual([
      { id: "what-it-does", title: "What it does" },
      { id: "tuning", title: "Tuning" },
    ]);
    expect(root.querySelector("h2")!.id).toBe("what-it-does");
  });
});

describe("parameterField", () => {
  it.each([
    ["warmup_temperature", "warmupTemperature"],
    ["tank1_enabled", "tank1Enabled"],
    ["main_fwd_minimum_pump_dutypoint", "mainFwdMinimumPumpDutypoint"],
  ])("names %s %s", (name, field) => expect(parameterField(name)).toBe(field));
});

describe("linkParameters", () => {
  it("links each mention of a parameter, its own row included, to the given address", () => {
    const root = document.createElement("article");
    root.innerHTML = `
      <p>Holds <code>warmup_temperature</code>, not <code>unknown_thing</code>.</p>
      <table class="parameters"><tbody><tr>
        <td><code>warmup_temperature</code></td><td>55 °C</td><td>Below <code>warmup_temperature</code>.</td>
      </tr></tbody></table>`;

    linkParameters(root, (field) => `/thrs/control/pvt?parameter=${field}`);

    const links = [...root.querySelectorAll("a")].map((link) => link.getAttribute("href"));
    expect(links).toEqual(Array(3).fill("/thrs/control/pvt?parameter=warmupTemperature"));
    expect(root.querySelector("p")!.textContent).toContain("unknown_thing");
  });
});

describe("checkManual", () => {
  const table = (name: string) =>
    `<table class="parameters"><tbody><tr><td><code>${name}</code></td></tr></tbody></table>`;

  it("finds nothing wrong with a manual the page shows as designed", async () => {
    const html = `<figure class="diagram"><pre class="mermaid">stateDiagram-v2
  state "Idle" as idle
  [*] --> idle</pre></figure>${table("warmup_temperature")}`;
    expect(await checkManual(html, "pvt")).toEqual([]);
  });

  it("reports a diagram that falls back to Mermaid, and why", async () => {
    const html = `<pre class="mermaid">stateDiagram-v2
  idle --> [*]</pre>`;
    const [problem] = await checkManual(html, "pvt");
    expect(problem).toContain(
      'State diagram 1 falls back to Mermaid instead of state cards: a final state, "idle --> [*]"',
    );
  });

  it("reports a parameter its Controls page has no row for", async () => {
    const [problem] = await checkManual(table("warmup_temprature"), "pvt");
    expect(problem).toContain("warmup_temprature has no row on the pvt Controls page");
  });

  it("does not check links for a module without a Controls page", async () => {
    expect(await checkManual(table("anything_at_all"), "pvt-main")).toEqual([]);
  });
});

// Every manual published to the Documentation tab draws its diagrams as state
// cards and links each parameter to its row on the Controls page.
const PUBLISHED = import.meta.glob<string>("../../documentation/*.html", {
  query: "?raw",
  import: "default",
  eager: true,
});

describe.each(Object.entries(PUBLISHED))("published manual %s", (path, html) => {
  it("shows as designed", async () => {
    const module = path.slice(path.lastIndexOf("/") + 1, -".html".length);
    expect(await checkManual(html, module)).toEqual([]);
  });
});
