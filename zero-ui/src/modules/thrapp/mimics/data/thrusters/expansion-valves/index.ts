import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionValve } from "../../helpers";

export const THRUSTERS_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-04": toExpansionValve("1041-04"),
  },
});
