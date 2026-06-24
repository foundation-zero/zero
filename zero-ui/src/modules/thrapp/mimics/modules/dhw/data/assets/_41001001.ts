import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HVAC>({
  controls: {
    controller: getField(ControlComponentType.PIDController, "dhw", "dhwDcFlowController"),
  },
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "dhw", "htBoostingTemperatureSetpoint"),
    flow: getField(ParametersType.Flow, "dhw", "dcFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHvacExchanger"),
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
    measurement: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "dhw-hvac-exchanger",
  }),
});
