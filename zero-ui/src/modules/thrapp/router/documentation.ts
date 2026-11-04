import { MimicKey } from "./mimics";

const MANUAL_FILES = import.meta.glob<string>("../documentation/*.html", {
  query: "?raw",
  import: "default",
});

const moduleOf = (path: string) => path.slice(path.lastIndexOf("/") + 1, -".html".length);

export const DOCUMENTATION: Partial<Record<MimicKey, () => Promise<string>>> = Object.fromEntries(
  Object.entries(MANUAL_FILES).map(([path, load]) => [moduleOf(path), load]),
);
