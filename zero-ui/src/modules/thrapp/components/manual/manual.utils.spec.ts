import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import { describe, expect, it } from "vitest";
import { linkParameters, outlineManual, paintModeBadges, readManualStamp } from "./manual.utils";

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

describe("linkParameters", () => {
  it("links each mention of a parameter to its row in the tuning table", () => {
    const root = document.createElement("article");
    root.innerHTML = `
      <p>Holds <code>warmup_temperature</code>, not <code>unknown_thing</code>.</p>
      <table class="parameters"><tbody><tr>
        <td><code>warmup_temperature</code></td><td>55 °C</td><td>Below <code>warmup_temperature</code>.</td>
      </tr></tbody></table>`;

    linkParameters(root);

    const row = root.querySelector("td > code")!;
    expect(row.id).toBe("parameter-warmup_temperature");
    expect(row.closest("a")).toBeNull();
    const links = [...root.querySelectorAll("a")].map((link) => link.getAttribute("href"));
    expect(links).toEqual(["#parameter-warmup_temperature", "#parameter-warmup_temperature"]);
  });
});
