import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";

export const pvtHeatDumpController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(ControllerStateComponentType.PIDController, "pvt", "pvtHeatDumpController"),
};
