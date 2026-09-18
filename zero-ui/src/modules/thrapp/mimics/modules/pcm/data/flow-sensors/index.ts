import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import { PickKeys, SchemaDefinition, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType.Flow>): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

const createFlowSensor = (
  field: PickKeys<
    ThrsDefinitions["pcm"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Flow>
  >,
  temperatureField: PickKeys<
    ThrsDefinitions["pcm"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Temperature>
  >,
) =>
  toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Flow, "pcm", field),
    sensors: {
      temperature: getField(SensorComponentType.Temperature, "pcm", temperatureField),
    },
    get tooltip() {
      return tooltip(this.source);
    },
  });

const createConsumerFlowSensor = (
  field: PickKeys<
    ThrsDefinitions["consumers"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Flow>
  >,
  temperatureField: PickKeys<
    ThrsDefinitions["consumers"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Temperature>
  >,
) =>
  toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Flow, "consumers", field),
    sensors: {
      temperature: getField(SensorComponentType.Temperature, "consumers", temperatureField),
    },
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const PCM_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-18": createFlowSensor("pcmFlowModule1", "pcmTemperatureModule1"),
    "1057-19": createFlowSensor("pcmFlowModule2", "pcmTemperatureModule2"),
    "1057-20": createFlowSensor("pcmFlowModule3", "pcmTemperatureModule3"),
    "1057-21": createFlowSensor("pcmFlowModule4", "pcmTemperatureModule4"),
    "1058-07-1": createConsumerFlowSensor("consumersFlowDhw", "consumersTemperatureDhwSupply"),
    "1058-07-2": createConsumerFlowSensor("consumersFlowDhw", "consumersTemperatureDhwSupply"),
    "1192": createConsumerFlowSensor("consumersFlowBypass", "consumersTemperatureDhwReturn"),
  },
});
