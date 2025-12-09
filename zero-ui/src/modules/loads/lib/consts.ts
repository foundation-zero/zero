import { VariableType } from "../types";

export const LOAD_UNIT: Record<VariableType, string> = {
  [VariableType.Percentage]: "%",
  [VariableType.Tonnes]: "t",
};
