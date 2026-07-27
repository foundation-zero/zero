import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../dhw/data/shared";

export default toInstance<MimicComponentType.ExchangeCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    circuitName: "Seawater",
  },
  parameters: {},
  source: getCustomField("thrusters", { technicalName: "thrusters-seawater-loop" }),
  sensors: {
    deltaT: getField(SensorComponentType.DeltaT, "thrusters", "thrustersTemperatureSupply"),
    flow: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
    incoming: getField(
      SensorComponentType.Temperature,
      "thrusters",
      "thrustersTemperatureRecoveryMix",
    ),
    outgoing: getField(SensorComponentType.Temperature, "thrusters", "thrustersTemperatureSupply"),
    heatExchanger: [
      SensorComponentType.HeatExchanger,
      "thrusters",
      "thrustersMixRecovery",
    ] as unknown as ModuleField<SensorComponentType.HeatExchanger, "thrusters">,
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Seawater",
      componentType: "Exchange circuit",
    });
  },
});
