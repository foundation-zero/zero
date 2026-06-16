import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1022 from "./_1022";

export const toPump = toInstance<MimicComponentType.Pump>;

export const BOILER_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1022": _1022,
  },
});
