import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionTank } from "../../helpers";

export const ADSORPTION_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1040-02": toExpansionTank("1040-02"),
    "1040-03": toExpansionTank("1040-03"),
  },
});
