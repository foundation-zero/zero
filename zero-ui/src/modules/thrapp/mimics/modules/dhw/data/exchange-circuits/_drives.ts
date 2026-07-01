import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Drives & shore",
  },
  parameters: {},
  source: undefined,
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "drivesDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "drivesTemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDrivesExchanger"),
  },
  tooltip: tooltip({
    title: "Drives & shore",
    technicalName: "drives",
  }),
});
