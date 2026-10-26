import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import _freshwater from "./_freshwater";
import _pvt from "./_pvt";
import _thrusters from "./_thrusters";

export const PCM_CONNECTING_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ConnectingCircuit]: {
    freshwater: _freshwater,
    pvt: _pvt,
    thrusters: _thrusters,
  },
});
