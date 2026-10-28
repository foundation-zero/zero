import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toMixValve, valveFields } from "../../helpers";

export const ADSORPTION_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1046-02": toMixValve(valveFields("adsorption", "adsorptionMixHot")),
    "1047-01": toMixValve(valveFields("adsorption", "adsorptionMixWaste")),
  },
});
