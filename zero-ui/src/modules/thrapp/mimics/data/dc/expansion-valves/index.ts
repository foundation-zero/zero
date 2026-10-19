import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionValve } from "../../helpers";

export const DC_EXPANSION_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ExpansionValve]: {
    "1041-06": toExpansionValve("1041-06"),
  },
});
