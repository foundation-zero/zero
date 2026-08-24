import { AWA, Range, VariableUnit } from "../types";
import { toNumRangeId, toRange } from "./utils";

export const LOAD_UNIT: Record<VariableUnit, string> = {
  [VariableUnit.Ratio]: "%",
  [VariableUnit.Tonne]: "t",
  [VariableUnit.Bool]: "",
  [VariableUnit.Mm]: "mm",
  [VariableUnit.Meter]: "m",
  [VariableUnit.Knots]: "kts",
  [VariableUnit.Degrees]: "°",
  [VariableUnit.MicroMeterPerMeter]: "µm/m",
  [VariableUnit.DegreeCelsius]: "°C",
  [VariableUnit.TonneMeter]: "tonne · m",
  [VariableUnit.Percent]: "%",
};

const UNIT_I18N_KEY: Record<string, string> = {
  tonne: "tonne",
  t_m: "t_m",
  um_m: "um_m",
  deg_c: "degC",
  m: "m",
};

export const formatUnit = (unit: string | null | undefined, t: (key: string) => string): string => {
  if (!unit) return "";
  const key = UNIT_I18N_KEY[unit];
  return key ? t(`loads.units.${key}`) : unit;
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
