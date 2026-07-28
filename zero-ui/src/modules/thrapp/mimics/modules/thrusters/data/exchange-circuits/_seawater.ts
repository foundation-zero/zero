import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Seawater",
  },
  parameters: {},
  source: getCustomField("thrusters", { technicalName: "thrusters-seawater-loop" }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"), // TODO
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
    incoming: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureRecoveryMix",
    ),
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
    heatExchanger: getField(
      SensorComponentType.HeatExchanger,
      "thrusters",
      "thrustersSeawaterExchanger",
    ),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Seawater",
      componentType: "Exchange circuit",
    });
  },
});
