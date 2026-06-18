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
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "boilers", "htBoostingTemperatureSetpoint"),
    flow: getField(ParametersType.Flow, "boilers", "lt1FlowcontrolMinimumSetpoint"),
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
    measurement: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt1"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "boilers-hvac-exchanger",
  }),
});
