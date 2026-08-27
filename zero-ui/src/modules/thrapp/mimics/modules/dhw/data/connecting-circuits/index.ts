import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _freshwater from "./_freshwater";

export const DHW_CONNECTING_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ConnectingCircuit]: {
    freshwater: _freshwater,
  },
});
