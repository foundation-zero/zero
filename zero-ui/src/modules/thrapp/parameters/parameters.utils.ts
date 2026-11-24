import { ThrsDefinitions } from "@/modules/thrapp/lib/consts";
import {
  ControllerStateComponentType,
  ParametersType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField, Placeholder } from "../mimics/providers";
import { PidControllerTuning } from "./parameters.types";

export const pidControllerTuning = <Module extends keyof ThrsDefinitions>(
  module: Module,
  type: SensorComponentType.Temperature | SensorComponentType.Flow,
  controller:
    | PickKeys<
        ThrsDefinitions[Module]["controllerState"],
        SchemaDefinition<ControllerStateComponentType.PIDController>
      >
    | Placeholder,
  parameter:
    | PickKeys<ThrsDefinitions[Module]["parameters"], SchemaDefinition<ParametersType.Tuning>>
    | Placeholder,
  transform?: (value: number) => number,
): PidControllerTuning => ({
  type,
  controller: getField(ControllerStateComponentType.PIDController, module, controller),
  parameter: getField(ParametersType.Tuning, module, parameter),
  transform,
});

const SELECTION_TIMEOUT = 10_000;
const HIGHLIGHT = 2_500;

/**
 * Selects a parameter on the Controls page, as a manual's link asks: scrolls its
 * row into view and highlights it for a moment. The page renders after its data
 * arrives, so this waits for the row to appear. Returns a function that stops waiting.
 */
export const selectParameter = (root: HTMLElement, field: string) => {
  const find = () => root.querySelector<HTMLElement>(`[data-parameter="${CSS.escape(field)}"]`);
  const select = (row: HTMLElement) => {
    // A PID card can be taller than the screen; show its title rather than its middle.
    const tall = row.offsetHeight > window.innerHeight / 2;
    row.scrollIntoView({ behavior: "smooth", block: tall ? "start" : "center" });
    row.dataset.selected = "";
    setTimeout(() => delete row.dataset.selected, HIGHLIGHT);
  };

  const row = find();
  if (row) {
    select(row);
    return () => {};
  }
  const observer = new MutationObserver(() => {
    const row = find();
    if (!row) return;
    stop();
    select(row);
  });
  const timeout = setTimeout(() => observer.disconnect(), SELECTION_TIMEOUT);
  const stop = () => {
    observer.disconnect();
    clearTimeout(timeout);
  };
  observer.observe(root, { childList: true, subtree: true });
  return stop;
};
