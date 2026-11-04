import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import { describe, expect, it } from "vitest";
import { paintModeBadges } from "./manual.utils";

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
