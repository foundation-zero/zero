import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _adsorption from "./_adsorption";
import _brightloop from "./_dc";
import _drives from "./_drives";
import _highTempLoop from "./_highTempLoop";

export const DHW_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    highTempLoop: _highTempLoop,
    brightloop: _brightloop,
    drives: _drives,
    adsorption: _adsorption,
  },
});
