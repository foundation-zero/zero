import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "boilers", "lt2Delta"),
    flow: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt2"),
    incoming: getField(SensorComponentType.Temperature, "boilers", "lt2TemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "boilers", "lt2TemperatureRecoveryReturn"),
  },
  tooltip: tooltip({
    title: "Brightloop",
    technicalName: "brightloop",
  }),
});
