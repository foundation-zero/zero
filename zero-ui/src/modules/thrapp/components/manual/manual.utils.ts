import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import diagramCss from "./manual-diagram.css?inline";
import { ManualSection, ManualStamp } from "./manual.types";

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

// Mirrors the stamp manual_version.py writes:
// <p class="version" data-module="pvt" data-facts="1e42533">Control version 1e42533 · 2026-11-04</p>
const STAMP = /data-facts="(?<version>[^"]+)"[^>]*>[^<]*·\s*(?<issued>\d{4}-\d{2}-\d{2})/;

export const readManualStamp = (html: string): ManualStamp | undefined => {
  const groups = STAMP.exec(html)?.groups;
  return groups ? { version: groups.version, issued: groups.issued } : undefined;
};

const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

/** The manual's sections, giving each heading an id to link to. */
export const outlineManual = (root: HTMLElement): Array<ManualSection> =>
  [...root.querySelectorAll<HTMLHeadingElement>("h2")].map((heading) => {
    const title = heading.textContent?.trim() ?? "";
    heading.id ||= slug(title);
    return { id: heading.id, title };
  });

export const parameterAnchor = (name: string) => `parameter-${name}`;

/** Links every mention of a parameter to its row in the tuning tables. */
export const linkParameters = (root: HTMLElement) => {
  const rows = root.querySelectorAll<HTMLElement>("table.parameters td:first-child > code");
  const names = new Set([...rows].map((code) => code.textContent!.trim()));
  rows.forEach((code) => (code.id = parameterAnchor(code.textContent!.trim())));

  root.querySelectorAll<HTMLElement>("code").forEach((code) => {
    const name = code.textContent!.trim();
    if (!names.has(name) || code.id || code.closest("a")) return;
    const link = document.createElement("a");
    link.href = `#${parameterAnchor(name)}`;
    code.replaceWith(link);
    link.append(code);
  });
};
