import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Drives & shore",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "Drives & shore",
    technicalName: "drives-and-shore",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "drivesDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "drivesFlowRecovery"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDrivesExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
