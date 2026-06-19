import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _brightloop from "./_brightloop";
import _drives from "./_drives";
import _fahrenheit from "./_fahrenheit";
import _highTempLoop from "./_highTempLoop";

export const BOILER_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.ExchangeCircuit]: {
    highTempLoop: _highTempLoop,
    brightloop: _brightloop,
    drives: _drives,
    fahrenheit: _fahrenheit,
  },
});
