import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionValve } from "../../helpers";

export const ADSORPTION_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-02": toExpansionValve("1041-02"),
    "1041-03": toExpansionValve("1041-03"),
  },
});
