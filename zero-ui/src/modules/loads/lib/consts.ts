import { Range, VariableType } from "../types";
import { toRange } from "./utils";

export const LOAD_UNIT: Record<VariableType, string> = {
  [VariableType.Percentage]: "%",
  [VariableType.Tonnes]: "t",
};

export const TWA_VALUES: Range[] = toRange(0, 40, 50, 60, 90, 12, 150);
export const TWS_VALUES: Range[] = toRange(0, 5, 10, 15, 20, 25, 30, 40, 50, Infinity);
