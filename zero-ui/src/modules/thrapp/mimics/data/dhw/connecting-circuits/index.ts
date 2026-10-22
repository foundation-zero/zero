import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import _freshwater from "./_freshwater";

export const DHW_CONNECTING_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.FreshwaterCircuit]: {
    freshwater: _freshwater,
  },
});
