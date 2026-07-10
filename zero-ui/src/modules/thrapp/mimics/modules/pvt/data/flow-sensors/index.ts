import {
  ControlComponentType,
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";

const pid = (name: string) =>
  [ControllerStateComponentType.PIDController, "pvt", name] as ModuleField<
    ControllerStateComponentType.PIDController,
    "pvt"
  >;

const flowParam = (name: string) =>
  [ParametersType.Flow, "pvt", name] as ModuleField<ParametersType.Flow, "pvt">;

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Flow sensor",
  itemName: "Flow sensor",
  yardTag,
  technicalName,
});

export const PVT_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1058-12": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      controllerState: {
        controller: pid("pvtMainFwdFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainFwdReturn",
        ),
      },
      tooltip: tooltip("1058-12", "pvt-flow-main-fwd-recovery"),
    }),
    "1058-13": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      controllerState: {
        controller: pid("pvtMainAftFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureMainAftReturn",
        ),
      },
      tooltip: tooltip("1058-13", "pvt-flow-main-aft-recovery"),
    }),
    "1057-03": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      controllerState: {
        controller: pid("pvtOwnersFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      sensors: {
        temperature: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersReturn"),
      },
      tooltip: tooltip("1057-03", "pvt-flow-owners-recovery"),
    }),
  },
});
