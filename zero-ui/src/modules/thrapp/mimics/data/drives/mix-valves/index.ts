import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toMixValve, valveFields } from "../../helpers";

export const DRIVES_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1046-01": toMixValve(valveFields("drives", "drivesMixExchanger")),
    "1046-03": toMixValve(valveFields("drives", "drivesMixRecovery")),
  },
});
