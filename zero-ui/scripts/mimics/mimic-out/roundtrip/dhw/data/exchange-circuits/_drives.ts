import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ExchangeCircuit>({
  custom: {
    circuitName: "Drives & shore",
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      title: "Drives & shore",
      technicalName: "drives-and-shore",
    }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "drivesDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "drivesFlowRecovery"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDrivesExchanger"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecoveryReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Exchange circuit",
    });
  },
});
