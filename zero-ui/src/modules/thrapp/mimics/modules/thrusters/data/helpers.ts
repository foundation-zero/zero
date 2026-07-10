import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { ControllerStateComponentType } from "@/modules/thrs/types";

export const thrustersPidController = (
  field: string,
): ModuleField<ControllerStateComponentType.PIDController, "thrusters"> => [
  ControllerStateComponentType.PIDController,
  "thrusters",
  field,
];
