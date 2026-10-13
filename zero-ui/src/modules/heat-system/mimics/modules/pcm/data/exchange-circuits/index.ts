import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _adsorption from "./_adsorption";
import _dhw from "./_dhw";

export const PCM_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    dhw: _dhw,
    adsorption: _adsorption,
  },
});
