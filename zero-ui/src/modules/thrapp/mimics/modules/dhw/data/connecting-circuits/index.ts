import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _freshwater from "./_freshwater";

export const DHW_FRESHWATER_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.FreshwaterCircuit]: {
    domestic: _freshwater,
  },
});
