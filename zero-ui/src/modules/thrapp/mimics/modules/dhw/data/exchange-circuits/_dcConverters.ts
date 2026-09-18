import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "DC Converters",
    modeModule: "dc",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "DC converters",
    technicalName: "dc-converters",
  }),
  sensors: {
    flow: getField(SensorComponentType.Flow, "dc", "dcFlowRecovery"),
    incoming: getField(SensorComponentType.Temperature, "dc", "dcTemperatureRecovery"),
    outgoing: getField(SensorComponentType.Temperature, "dc", "dcTemperatureRecoveryReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dc", "dcDhwExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
