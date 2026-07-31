import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1074 from "./_1074";
import _1091_01 from "./_1091_01";
import _1091_02 from "./_1091_02";
import _1214_01 from "./_1214_01";

export const THRUSTERS_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1214-01": _1214_01,
    "1074": _1074,
  },
  [MimicComponentType.ThreeWaySwitchValve]: {
    "1091-01": _1091_01,
    "1091-02": _1091_02,
  },
});
