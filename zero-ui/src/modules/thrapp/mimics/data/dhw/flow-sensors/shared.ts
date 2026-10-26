import { getField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType } from "@/modules/thrsim/types";

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
