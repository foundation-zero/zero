import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.ExchangeCircuit>({
  custom: {
    circuitName: "Seawater",
  },
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("thrusters", {
      technicalName: "thrusters-seawater-loop",
    }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"),
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
    heatExchanger: getField(SensorComponentType.HeatExchanger, "thrusters", "thrustersSeawaterExchanger"),
    incoming: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureRecoveryMix"),
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Seawater",
      componentType: "Exchange circuit",
    });
  },
});
