import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toExpansionTank } from "../../helpers";

export const PVT_EXPANSION_TANK_DATA = toFieldsMap({
  [MimicComponentType.ExpansionTank]: {
    "1040-01": toExpansionTank("1040-01"),
  },
});
