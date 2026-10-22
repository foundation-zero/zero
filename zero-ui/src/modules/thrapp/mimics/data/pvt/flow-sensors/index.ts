import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toFlowSensor } from "../../helpers";
import { PVT_AFT_FLOW_SENSORS } from "./_aft";

export const PVT_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1058-12": toFlowSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainFwdReturn",
        ),
      },
    }),
    "1058-13": toFlowSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainAftReturn",
        ),
      },
    }),
    "1057-03": toFlowSensor({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      sensors: {
        temperature: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
    }),
    ...PVT_AFT_FLOW_SENSORS,
  },
});
