import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1035 from "./_1035";
import _41001001 from "./_41001001";

export const BOILER_ASSET_DATA = toFieldsMap({
  [MimicComponentType.HeatPump]: {
    "1035": _1035,
  },
  [MimicComponentType.HVAC]: {
    "41001001": _41001001,
  },
});
