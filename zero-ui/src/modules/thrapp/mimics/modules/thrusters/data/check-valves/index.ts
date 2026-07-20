import { toFieldsMap } from "../../..";
import { MimicComponentType } from "../../../../../types";
import _1213_01 from "./_1213_01";
import _1213_02 from "./_1213_02";
import _1217_01 from "./_1217_01";
import _1217_02 from "./_1217_02";

export const THRUSTERS_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: {
    "1213-01": _1213_01,
    "1213-02": _1213_02,
    "1217-01": _1217_01,
    "1217-02": _1217_02,
  },
});
