import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Domestic hot water",
    modeModule: "dhw",
  },
  parameters: {},
  source: getCustomField("dhw", {
    title: "Domestic hot water",
    technicalName: "dhw",
  }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "placeholder"),
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwConsumersExchanger"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
