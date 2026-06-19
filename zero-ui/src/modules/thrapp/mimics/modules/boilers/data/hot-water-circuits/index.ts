import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _domestic from "./_domestic";

export const BOILER_HOT_WATER_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.HotWaterCircuit]: {
    domestic: _domestic,
  },
});
