import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import _pcm from "../connecting-circuits/_pcm";
import _seawater from "./_seawater";

export const THRUSTERS_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: _seawater,
  },
  [MimicComponentType.ConnectingCircuit]: {
    pcm: _pcm,
  },
});
