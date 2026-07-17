import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _pcm from "./_pcm";
import _seawater from "./_seawater";

export const THRUSTERS_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    seawater: _seawater,
  },
  [MimicComponentType.HotWaterCircuit]: {
    pcm: _pcm,
  },
});
