import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _pcm from "./_pcm";
import _seawater from "./_seawater";

export const THRUSTERS_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.FreshwaterCircuit]: {
    "pcm": _pcm,
  },
  [MimicComponentType.ExchangeCircuit]: {
    "seawater": _seawater,
  },
});
