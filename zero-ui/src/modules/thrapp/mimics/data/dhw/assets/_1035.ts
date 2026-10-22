import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";
import { pumpFlowController } from "../controllers";

export default toInstance<MimicComponentType.HeatPump>({
  controls: {
    heatpump: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
  },
  controllerState: { controller: pumpFlowController },
  source: getField(SensorComponentType.HeatPump, "dhw", "dhwHeatpump"),
  custom: { controller: pumpFlowController },
  parameters: {
    temperatureSetpoint: getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint"),
  },
  sensors: {
    heatTransfer: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwHeatpumpHeat"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat pump",
      componentType: "Heat pump",
    });
  },
});
