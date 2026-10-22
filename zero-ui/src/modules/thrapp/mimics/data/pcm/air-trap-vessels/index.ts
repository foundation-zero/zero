import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toAirTrapVessel } from "../../helpers";

export const PCM_AIR_TRAP_VESSEL_DATA = toFieldsMap({
  [MimicComponentType.AirTrapVessel]: {
    "1084": toAirTrapVessel("1084"),
  },
});
