import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toMixValve, valveFields } from "../../helpers";

export const DC_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1043-02": toMixValve(valveFields("dc", "dcMixAft")),
    "1042-03": toMixValve(valveFields("dc", "dcMixFwd")),
    "1045-01": toMixValve(valveFields("dc", "dcMixUgrid")),
    "1046-04": toMixValve(valveFields("dc", "dcMixRecovery")),
    "1046-05": toMixValve(valveFields("dc", "dcMixExchanger")),
  },
});
