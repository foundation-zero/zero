import { getField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType } from "@/modules/thrapp/types/thrs";

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
