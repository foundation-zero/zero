import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toSwitchValve, valveFields } from "../../helpers";

export const ADSORPTION_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1187-01": toSwitchValve(valveFields("adsorption", "adsorptionSwitchDhw")),
  },
});
