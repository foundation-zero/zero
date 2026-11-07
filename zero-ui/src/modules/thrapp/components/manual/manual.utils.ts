import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";

// The diagram's Mermaid source; zero-thrs-control renders it to the SVG shown in its place.
const MERMAID_BLOCK = /<pre class="mermaid">[\s\S]*?<\/pre>/;

export const paintModes = (root: HTMLElement) => {
  root.querySelectorAll<HTMLElement>("[data-mode]").forEach((badge) => {
    badge.style.backgroundColor = MODE_COLORS[badge.dataset.mode as ModeBadgeMode] ?? "";
  });
  Object.entries(MODE_COLORS).forEach(([mode, color]) =>
    root.querySelectorAll<SVGElement>(`.node.${mode} rect`).forEach((state) => {
      state.style.stroke = color;
      state.style.strokeWidth = "2px";
    }),
  );
};

export const withDiagram = (html: string, svg: string) => html.replace(MERMAID_BLOCK, () => svg);
