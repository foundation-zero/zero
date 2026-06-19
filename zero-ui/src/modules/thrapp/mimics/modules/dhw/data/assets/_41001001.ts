import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HVAC>({
  controls: {
    heatExchanger: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
    controller: getField(ControlComponentType.PIDController, "dhw", "dhwDrivesFlowController"),
  },
  custom: {},
  parameters: {
    temperature: getField(ParametersType.Temperature, "dhw", "htBoostingTemperatureSetpoint"),
    flow: getField(ParametersType.Flow, "dhw", "drivesFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHvacExchanger"),
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHvacExchanger"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
    measurement: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "dhw-hvac-exchanger",
  }),
});
