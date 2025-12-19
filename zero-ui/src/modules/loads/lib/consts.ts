import { Range, VariableUnit } from "../types";
import { toRange } from "./utils";

export const LOAD_UNIT: Record<VariableUnit, string> = {
  [VariableUnit.Percentage]: "%",
  [VariableUnit.Tonne]: "t",
  [VariableUnit.OnOff]: "",
};

export const AWA_VALUES: Range[] = toRange(0, 40, 50, 60, 90, 12, 150);
export const AWS_VALUES: Range[] = toRange(0, 5, 10, 15, 20, 25, 30, 40, 50, Infinity);
