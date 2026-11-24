import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import diagramCss from "./manual-diagram.css?inline";
import { ManualSection, ManualStamp } from "./manual.types";
import { diagramSource, drawStateDiagram, stateDiagramProblem } from "./state-diagram";

const modeStateCss = Object.entries(MODE_COLORS)
  .map(([mode, color]) => `.node.${mode} rect { stroke: ${color}; stroke-width: 2px; }`)
  .join("\n");

export const paintModeBadges = (root: HTMLElement) =>
  root.querySelectorAll<HTMLElement>("[data-mode]").forEach((badge) => {
    badge.style.backgroundColor = MODE_COLORS[badge.dataset.mode as ModeBadgeMode] ?? "";
  });

export type DecorateOptions = {
  /** Shrink state diagrams wider than the page to fit it, rather than scroll them. */
  fitDiagrams?: boolean;
};

/** Draws state diagrams as cards; Mermaid draws the ones using syntax the cards do not cover. */
export const renderDiagrams = async (root: HTMLElement, { fitDiagrams }: DecorateOptions = {}) => {
  const sources = [...root.querySelectorAll<HTMLElement>("pre.mermaid:not([data-processed])")];
  const drawn = await Promise.all(
    sources.map((pre) => drawStateDiagram(pre, { fit: fitDiagrams })),
  );
  const diagrams = sources.filter((_, i) => !drawn[i]);
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

export const decorateManual = async (root: HTMLElement, options: DecorateOptions = {}) => {
  paintModeBadges(root);
  await renderDiagrams(root, options);
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

/** The control's name for a parameter the manual names as the Python does: `tank1_enabled` is `tank1Enabled`. */
export const parameterField = (name: string) =>
  name.replace(/_([a-z0-9])/g, (_, next: string) => next.toUpperCase());

/** The parameters a manual documents: the names in the first column of its tuning tables. */
export const manualParameters = (root: ParentNode) =>
  [...root.querySelectorAll("table.parameters td:first-child > code")].map((code) =>
    code.textContent!.trim(),
  );

/**
 * Links every mention of a parameter, in the text and in the tuning tables, to
 * `href(field)`. A parameter is a name listed in the first column of a tuning table.
 */
export const linkParameters = (root: HTMLElement, href: (field: string) => string) => {
  const names = new Set(manualParameters(root));

  root.querySelectorAll<HTMLElement>("code").forEach((code) => {
    const name = code.textContent!.trim();
    if (!names.has(name) || code.closest("a")) return;
    const link = document.createElement("a");
    link.href = href(parameterField(name));
    code.replaceWith(link);
    link.append(code);
  });
};

// Every Controls page's source, read only when a manual is checked.
const CONTROLS_SOURCES = import.meta.glob<string>("../../parameters/modules/*/**/*.vue", {
  query: "?raw",
  import: "default",
});
// A field is named in a Controls page as a string: getField(…, "pvt", "warmupTemperature").
const QUOTED_NAME = /["'`]([a-z][A-Za-z0-9]*)["'`]/g;

/** The fields a module's Controls page shows, or undefined when the module has none. */
export const controlsFields = async (module: string) => {
  const loads = Object.entries(CONTROLS_SOURCES)
    .filter(([path]) => path.includes(`/parameters/modules/${module}/`))
    .map(([, load]) => load());
  if (loads.length === 0) return undefined;
  const sources = await Promise.all(loads);
  return new Set(
    sources.flatMap((source) => [...source.matchAll(QUOTED_NAME)].map(([, name]) => name)),
  );
};

/**
 * What would keep a manual from showing as designed: a state diagram the cards
 * cannot draw, which falls back to Mermaid, or a parameter its module's Controls
 * page has no row for, whose link would select nothing. Empty when there is none.
 */
export const checkManual = async (html: string, module: string): Promise<Array<string>> => {
  const fragment = document.createElement("template");
  fragment.innerHTML = html;
  const root = fragment.content;

  const diagrams = [...root.querySelectorAll("pre.mermaid")].flatMap((pre, i) => {
    const problem = stateDiagramProblem(diagramSource(pre));
    return problem
      ? [
          `State diagram ${i + 1} falls back to Mermaid instead of state cards: ${problem}. ` +
            "Keep to the syntax in the thrs-module-manual skill's references/template.md.",
        ]
      : [];
  });

  const fields = await controlsFields(module);
  const unlinked = fields
    ? manualParameters(root).filter((name) => !fields.has(parameterField(name)))
    : [];
  const parameters = [...new Set(unlinked)].map(
    (name) =>
      `${name} has no row on the ${module} Controls page, so its link would select nothing. ` +
      "Check the name against the control, or add the parameter to the Controls page.",
  );
  return [...diagrams, ...parameters];
};
