import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HeatPump>({
  controls: {
    heatExchanger: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
    controller: getField(ControlComponentType.PIDController, "dhw", "dhwPumpFlowController"),
  },
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "dhw", "heatpumpTemperatureSetpoint"),
    flow: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
  },
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    measurement: getField(SensorComponentType.Flow, "dhw", "dhwFlowBoosting"),
  },
  tooltip: tooltip({
    title: "Heat Pump",
    yardTag: "1035",
    technicalName: "dhw-heatpump",
  }),
});
