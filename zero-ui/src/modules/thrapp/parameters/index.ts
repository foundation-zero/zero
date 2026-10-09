import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import {
  ControllerStateComponentType,
  ParametersType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { getField, ModuleField, Placeholder } from "../mimics/providers";

export type PidControllerTuning = {
  type: SensorComponentType.Temperature | SensorComponentType.Flow;
  controller: ModuleField<ControllerStateComponentType.PIDController>;
  parameter: ModuleField<ParametersType.Tuning>;
};

export const pidControllerTuning = <Module extends keyof ThrsDefinitions>(
  module: Module,
  type: SensorComponentType.Temperature | SensorComponentType.Flow,
  controller:
    | PickKeys<
        ThrsDefinitions[Module]["controllerState"],
        SchemaDefinition<ControllerStateComponentType.PIDController>
      >
    | Placeholder,
  parameter:
    | PickKeys<ThrsDefinitions[Module]["parameters"], SchemaDefinition<ParametersType.Tuning>>
    | Placeholder,
): PidControllerTuning => ({
  type,
  controller: getField(ControllerStateComponentType.PIDController, module, controller),
  parameter: getField(ParametersType.Tuning, module, parameter),
});
