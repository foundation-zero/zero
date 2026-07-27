import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "DC Converters",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "DC converters",
    technicalName: "dc-converters",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "dcDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dcTemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwDcExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
