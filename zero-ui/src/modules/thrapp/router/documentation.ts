import { loadManual } from "@/modules/thrapp/components/manual";
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

export const DOCUMENTATION: Partial<Record<MimicKey, () => Promise<string>>> = Object.fromEntries(
  Object.entries(MANUAL_FILES).map(([path, loadHtml]) => [
    moduleOf(path),
    () => loadManual(loadHtml, DIAGRAM_FILES[diagramOf(path)]),
  ]),
);
