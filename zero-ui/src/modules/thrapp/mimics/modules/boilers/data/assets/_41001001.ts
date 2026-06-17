import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HVAC>({
  controls: {
    heatExchanger: getField(ControlComponentType.Heatpump, "boilers", "boilersHeatpump"),
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt1FlowController"),
  },
  custom: {
    controllerName: "HVAC controller",
    setpointName: "Heatpump flow parameter",
  },
  parameters: {
    temperature: getField(ParametersType.Temperature, "boilers", "htBoostingTemperatureSetpoint"),
  },
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "boilers", "boilersHvacExchanger"),
    incoming: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureFahrenheitReturn",
    ),
    outgoing: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureHvacExchangerReturn",
    ),
    measurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowBoosting"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "boilers-hvac-exchanger",
  }),
});
