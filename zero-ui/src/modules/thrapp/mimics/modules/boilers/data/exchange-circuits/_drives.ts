import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {
    circuitName: "Drives circuit",
  },
  parameters: {},
  source: undefined,
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "boilers", "lt1Delta"),
    flow: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt1"),
    incoming: getField(SensorComponentType.Temperature, "boilers", "lt1TemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "boilers", "lt1TemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "boilers", "boilersLt1Exchanger"),
  },
  tooltip: tooltip({
    title: "Drives",
    technicalName: "drives",
  }),
});
