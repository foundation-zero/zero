import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import diagramCss from "./manual-diagram.css?inline";

const modeStateCss = Object.entries(MODE_COLORS)
  .map(([mode, color]) => `.node.${mode} rect { stroke: ${color}; stroke-width: 2px; }`)
  .join("\n");

export const paintModeBadges = (root: HTMLElement) =>
  root.querySelectorAll<HTMLElement>("[data-mode]").forEach((badge) => {
    badge.style.backgroundColor = MODE_COLORS[badge.dataset.mode as ModeBadgeMode] ?? "";
  });

export const renderDiagrams = async (root: HTMLElement) => {
  const diagrams = [...root.querySelectorAll<HTMLElement>("pre.mermaid:not([data-processed])")];
  if (diagrams.length === 0) return;

  const { default: mermaid } = await import("mermaid");
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    fontFamily: "Inter, sans-serif",
    themeCSS: `${diagramCss}\n${modeStateCss}`,
    state: { useMaxWidth: true },
  });
  await mermaid.run({ nodes: diagrams });
};

export const decorateManual = async (root: HTMLElement) => {
  paintModeBadges(root);
  await renderDiagrams(root);
};
