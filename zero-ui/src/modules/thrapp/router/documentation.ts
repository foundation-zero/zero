import { withDiagram } from "@/modules/thrapp/components/manual";
import { MimicKey } from "./mimics";

const MANUAL_FILES = import.meta.glob<string>("../documentation/*.html", {
  query: "?raw",
  import: "default",
});
const DIAGRAM_FILES = import.meta.glob<string>("../documentation/*.svg", {
  query: "?raw",
  import: "default",
});

const moduleOf = (path: string) => path.slice(path.lastIndexOf("/") + 1, -".html".length);
const diagramOf = (manualPath: string) => manualPath.replace(/\.html$/, ".svg");

const loadManual = async (manualPath: string) => {
  const [html, diagram] = await Promise.all([
    MANUAL_FILES[manualPath](),
    DIAGRAM_FILES[diagramOf(manualPath)](),
  ]);
  return withDiagram(html, diagram);
};

export const DOCUMENTATION: Partial<Record<MimicKey, () => Promise<string>>> = Object.fromEntries(
  Object.keys(MANUAL_FILES).map((path) => [moduleOf(path), () => loadManual(path)]),
);
