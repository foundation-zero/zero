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
    modeModule: "drives",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "Drives & shore",
    technicalName: "drives-and-shore",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "drivesDelta"),
    flow: getField(SensorComponentType.Flow, "drives", "drivesFlowRecovery"),
    incoming: getField(SensorComponentType.Temperature, "drives", "drivesTemperatureRecovery"),
    outgoing: getField(
      SensorComponentType.Temperature,
      "drives",
      "drivesTemperatureRecoveryReturn",
    ),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "drives", "drivesDhwExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
