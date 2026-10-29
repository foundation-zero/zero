import { ThrsDefinitions } from "@/modules/thrapp/lib/consts";
import {
  ControllerStateComponentType,
  ParametersType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { getField, Placeholder } from "../mimics/providers";
import { PidControllerTuning } from "./parameters.types";

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
  transform?: (value: number) => number,
): PidControllerTuning => ({
  type,
  controller: getField(ControllerStateComponentType.PIDController, module, controller),
  parameter: getField(ParametersType.Tuning, module, parameter),
  transform,
});
