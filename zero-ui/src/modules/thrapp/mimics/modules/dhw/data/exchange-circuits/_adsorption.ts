import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  custom: {
    circuitName: "Adsorption circuit",
  },
  parameters: {},
  source: undefined,
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"),
    flow: getField(SensorComponentType.Flow, "dhw", "adsorptionFlowDhw"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureWasteReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "adsorptionTemperatureDhwReturn"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwAdsorptionExchanger"),
  },
  tooltip: tooltip({
    title: "Adsorption",
    technicalName: "adsorption",
  }),
});
