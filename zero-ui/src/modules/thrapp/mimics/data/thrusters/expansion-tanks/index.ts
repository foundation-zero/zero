import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionTank } from "../../helpers";

export const THRUSTERS_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1092": toExpansionTank("1092"),
  },
});
