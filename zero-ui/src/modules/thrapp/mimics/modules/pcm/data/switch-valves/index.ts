import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import {
  ControlComponentType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const createSwitchValve = <Module extends keyof ThrsDefinitions>(
  module: Module,
  field: PickKeys<
    ThrsDefinitions[Module]["controlValues"],
    SchemaDefinition<ControlComponentType.Valve>
  >,
) =>
  toInstance<MimicComponentType.SwitchValve>({
    controls: { valve: getField(ControlComponentType.Valve, module, field) },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(
      SensorComponentType.Valve,
      module,
      field as PickKeys<
        ThrsDefinitions[Module]["sensorValues"],
        SchemaDefinition<SensorComponentType.Valve>
      >,
    ),
    sensors: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Switch valve",
        componentType: "Switch valve",
      });
    },
  });

export const PCM_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1190-01": createSwitchValve("pcm", "pcmSwitchChargingSupply"),
    "1066-01": createSwitchValve("pcm", "pcmSwitchDischarging"),
    "1062-02": createSwitchValve("pcm", "pcmSwitchChargingReturn"),
    "1066-02": createSwitchValve("consumers", "consumersSwitchAdsorption"),
    "1067-15": createSwitchValve("consumers", "consumersSwitchDhw"),
    "1071-02": createSwitchValve("pcm", "pcmSwitchConsumers"),
  },
});
