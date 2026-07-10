import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { thrustersPidController } from "../helpers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Flow sensor",
  itemName: "Flow sensor",
  yardTag,
  technicalName,
});

export const THRUSTERS_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-22": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump2"),
      },
      controllerState: {
        controller: thrustersPidController("fwdFlowBalanceController"),
      },
      custom: {},
      parameters: {
        flow: getField(ParametersType.Flow, "thrusters", "thrustersMaximumFlow"),
      },
      source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowFwd"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureFwd",
        ),
      },
      tooltip: tooltip("1057-22", "thrusters-flow-fwd"),
    }),
    "1218-01": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
      },
      controllerState: {
        controller: thrustersPidController("recoveryFlowController"),
      },
      custom: {},
      parameters: {
        flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
      },
      source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowRecovery"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureRecoveryMix",
        ),
      },
      tooltip: tooltip("1218-01", "thrusters-flow-recovery"),
    }),
    "1218-02": toInstance<MimicComponentType.FlowSensor>({
      controls: {
        pump: getField(ControlComponentType.Pump, "thrusters", "thrustersPump1"),
      },
      controllerState: {
        controller: thrustersPidController("aftFlowBalanceController"),
      },
      custom: {},
      parameters: {
        flow: getField(ParametersType.Flow, "thrusters", "thrustersMinimumFlow"),
      },
      source: getField(SensorComponentType.Flow, "thrusters", "thrustersFlowAft"),
      sensors: {
        temperature: getField(
          SensorComponentType.Temperature,
          "thrusters",
          "thrustersTemperatureAft",
        ),
      },
      tooltip: tooltip("1218-02", "thrusters-flow-aft"),
    }),
  },
});
