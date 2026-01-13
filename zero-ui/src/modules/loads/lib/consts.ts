import { AWA, Range, VariableUnit } from "../types";
import { toNumRangeId, toRange } from "./utils";

export const LOAD_UNIT: Record<VariableUnit, string> = {
  [VariableUnit.Ratio]: "%",
  [VariableUnit.Tonne]: "t",
  [VariableUnit.Bool]: "",
};

const AWAS = [AWA.Upwind, AWA.Reaching, AWA.Downwind];
export const AWA_VALUES: Range<AWA>[] = toRange(
  (_from, _to, index) => AWAS[index],
  0,
  60,
  120,
  180,
);
export const AWS_VALUES: Range[] = toRange(
  toNumRangeId("aws"),
  0,
  10,
  15,
  20,
  25,
  30,
  40,
  Infinity,
);
