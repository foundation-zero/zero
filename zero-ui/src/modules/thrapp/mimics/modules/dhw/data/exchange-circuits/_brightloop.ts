import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {
    circuitName: "Brightloop circuit",
  },
  parameters: {},
  source: undefined,
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "dcDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDcExchanger"),
  },
  tooltip: tooltip({
    title: "Brightloop",
    technicalName: "brightloop",
  }),
});
