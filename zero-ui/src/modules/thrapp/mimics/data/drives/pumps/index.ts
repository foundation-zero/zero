import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { pumpFields, toPump } from "../../helpers";

export const DRIVES_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1028": toPump(pumpFields("drives", "drivesPump1"), { componentType: "Pump" }),
    "1029": toPump(pumpFields("drives", "drivesPump2"), { componentType: "Pump" }),
  },
});
