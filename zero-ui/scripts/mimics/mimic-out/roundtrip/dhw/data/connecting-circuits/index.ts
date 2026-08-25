import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _domestic from "./_domestic";

export const DHW_FRESHWATER_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.FreshwaterCircuit]: {
    "domestic": _domestic,
  },
});
