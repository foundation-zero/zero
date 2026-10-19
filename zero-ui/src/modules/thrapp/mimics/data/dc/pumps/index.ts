import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { pumpFields, toPump } from "../../helpers";

export const DC_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1020": toPump(pumpFields("dc", "dcPumpAft"), { componentType: "Pump" }),
    "1023": toPump(pumpFields("dc", "dcPumpUgrid"), { componentType: "Pump" }),
    "1025": toPump(pumpFields("dc", "dcPumpFwd"), { componentType: "Pump" }),
  },
});
