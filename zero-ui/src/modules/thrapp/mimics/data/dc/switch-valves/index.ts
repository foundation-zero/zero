import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toSwitchValve, valveFields } from "../../helpers";

export const DC_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1068-01": toSwitchValve(valveFields("dc", "dcSwitchAft4")),
    "1068-02": toSwitchValve(valveFields("dc", "dcSwitchAft3")),
    "1068-03": toSwitchValve(valveFields("dc", "dcSwitchAft2")),
    "1068-04": toSwitchValve(valveFields("dc", "dcSwitchAft1")),
    "1068-05": toSwitchValve(valveFields("dc", "dcSwitchFwd2")),
    "1068-06": toSwitchValve(valveFields("dc", "dcSwitchFwd1")),
    "1069-02": toSwitchValve(valveFields("dc", "dcSwitchUgrid2")),
    "1069-03": toSwitchValve(valveFields("dc", "dcSwitchUgrid1")),
  },
});
