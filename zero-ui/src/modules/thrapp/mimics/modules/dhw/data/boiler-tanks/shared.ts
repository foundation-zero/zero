import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types";

import { ExtractModuleFields, ParameterFieldDefinitions } from "@/modules/thrapp/types/fields";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

export const controller = getField(
  ControllerStateComponentType.DhwTanksController,
  "dhw",
  "dhwTanksController",
);

export const boostingSupply = getField(
  SensorComponentType.Temperature,
  "dhw",
  "dhwTemperatureBoostingSupply",
);

export type BoilerTankParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.BoilerTank]
>;

export const parameters: BoilerTankParameters = {
  minimumLevel: getField(ParametersType.Level, "dhw", "minimumTankLevel"),
  maximumLevel: getField(ParametersType.Level, "dhw", "maximumTankLevel"),
  minimumTemperature: getField(ParametersType.Temperature, "dhw", "minimumTankTemperature"),
  maximumTemperature: getField(ParametersType.Temperature, "dhw", "maximumTankTemperature"),
};
