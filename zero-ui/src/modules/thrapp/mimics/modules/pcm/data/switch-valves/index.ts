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

const createPcmSwitchValve = (
  field: PickKeys<
    ThrsDefinitions["pcm"]["controlValues"],
    SchemaDefinition<ControlComponentType.Valve>
  >,
) =>
  toInstance<MimicComponentType.SwitchValve>({
    controls: { valve: getField(ControlComponentType.Valve, "pcm", field) },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Valve, "pcm", field),
    sensors: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Switch valve",
        componentType: "Switch valve",
      });
    },
  });

const createConsumersSwitchValve = (
  field: PickKeys<
    ThrsDefinitions["consumers"]["controlValues"],
    SchemaDefinition<ControlComponentType.Valve>
  >,
) =>
  toInstance<MimicComponentType.SwitchValve>({
    controls: { valve: getField(ControlComponentType.Valve, "consumers", field) },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Valve, "consumers", field),
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
    "1190-01": createPcmSwitchValve("pcmSwitchChargingSupply"),
    "1066-01": createPcmSwitchValve("pcmSwitchDischarging"),
    "1062-02": createPcmSwitchValve("pcmSwitchChargingReturn"),
    "1066-02": createConsumersSwitchValve("consumersSwitchAdsorption"),
    "1067-15": createConsumersSwitchValve("consumersSwitchDhw"),
    "1071-02": createPcmSwitchValve("pcmSwitchConsumers"),
  },
});
