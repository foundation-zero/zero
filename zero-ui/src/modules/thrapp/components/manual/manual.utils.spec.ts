import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import { describe, expect, it } from "vitest";
import { paintModes, withDiagram } from "./manual.utils";

describe("paintModes", () => {
  it("colors each mode badge like the mimic ModeBadge", () => {
    const root = document.createElement("article");
    root.innerHTML = `<span data-mode="Filling">filling</span><span data-mode="Unknown">x</span>`;

    paintModes(root);

    const [filling, unknown] = root.querySelectorAll<HTMLElement>("[data-mode]");
    expect(filling.style.backgroundColor).toBe(MODE_COLORS[ModeBadgeMode.Filling]);
    expect(unknown.style.backgroundColor).toBe("");
  });

  it("outlines each diagram state in its mode's color", () => {
    const root = document.createElement("article");
    root.innerHTML = `<svg><g class="node Boosting"><rect /></g><g class="node"><rect /></g></svg>`;

    paintModes(root);

    const [boosting, plain] = root.querySelectorAll<SVGElement>("rect");
    expect(boosting.style.stroke).toBe(MODE_COLORS[ModeBadgeMode.Boosting]);
    expect(boosting.style.strokeWidth).toBe("2px");
    expect(plain.style.stroke).toBe("");
  });
});

describe("withDiagram", () => {
  it("shows the rendered diagram in place of its Mermaid source", () => {
    const manual = `<figure class="diagram"><pre class="mermaid">\n[*] --> idle\n</pre></figure>`;

    expect(withDiagram(manual, "<svg>$&</svg>")).toBe(
      `<figure class="diagram"><svg>$&</svg></figure>`,
    );
  });
});
