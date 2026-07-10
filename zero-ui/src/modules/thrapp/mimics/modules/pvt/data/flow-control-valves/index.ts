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
  title: "Flow control valve",
  itemName: "Flow control valve",
  yardTag,
  technicalName,
});

export const PVT_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1018": toInstance<MimicComponentType.FlowControlValve>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainFwd"),
      },
      controllerState: {
        controller: pid("pvtMainFwdFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainFwdMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainFwd"),
      sensors: {
        measurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
      },
      tooltip: tooltip("1018", "pvt-flow-control-main-fwd"),
    }),
    "1019": toInstance<MimicComponentType.FlowControlValve>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainAft"),
      },
      controllerState: {
        controller: pid("pvtMainAftFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("mainAftMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainAft"),
      sensors: {
        measurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainAftRecovery"),
      },
      tooltip: tooltip("1019", "pvt-flow-control-main-aft"),
    }),
    "1021": toInstance<MimicComponentType.FlowControlValve>({
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixOwners"),
      },
      controllerState: {
        controller: pid("pvtOwnersFlowController"),
      },
      custom: {},
      parameters: {
        flow: flowParam("ownersMinimumPumpDutypoint"),
      },
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixOwners"),
      sensors: {
        measurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersRecovery"),
      },
      tooltip: tooltip("1021", "pvt-flow-control-owners"),
    }),
  },
});
