import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toSwitchValve, valveFields } from "../../helpers";

export const DRIVES_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1069-09": toSwitchValve(valveFields("drives", "drivesSwitchPropdriveAft2")),
    "1069-06": toSwitchValve(valveFields("drives", "drivesSwitchPropdriveAft1")),
    "1069-08": toSwitchValve(valveFields("drives", "drivesSwitchPropdriveFwd2")),
    "1069-07": toSwitchValve(valveFields("drives", "drivesSwitchPropdriveFwd1")),
    "1069-04": toSwitchValve(valveFields("drives", "drivesSwitchShorepowerSupply")),
    "1069-05": toSwitchValve(valveFields("drives", "drivesSwitchShorepowerReturn")),
  },
});
