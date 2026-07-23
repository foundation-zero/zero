import { getField } from "@/modules/thrapp/mimics/providers";
import { PIDController } from "@/modules/thrapp/types/fields";
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";

export const pvtMainFwdFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainFwdFlowController",
  ),
};

export const pvtMainAftFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtMainAftFlowController",
  ),
};

export const pvtOwnersFlowController: PIDController<SensorComponentType.Flow> = {
  type: SensorComponentType.Flow,
  controller: getField(
    ControllerStateComponentType.PIDController,
    "pvt",
    "pvtOwnersFlowController",
  ),
};
