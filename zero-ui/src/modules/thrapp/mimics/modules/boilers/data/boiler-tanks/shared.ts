import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";

import { ExtractModuleFields, ParameterFieldDefinitions } from "@/modules/thrapp/types/fields";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

export const controller = getField(
  ControlComponentType.BoilersTanksController,
  "boilers",
  "boilersTanksController",
);

export const boostingSupply = getField(
  SensorComponentType.Temperature,
  "boilers",
  "boilersTemperatureBoostingSupply",
);

export type BoilerTankParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.BoilerTank]
>;

export const parameters: BoilerTankParameters = {
  minimumLevel: getField(ParametersType.Level, "boilers", "minimumTankLevel"),
  maximumLevel: getField(ParametersType.Level, "boilers", "maximumTankLevel"),
  minimumTemperature: getField(ParametersType.Temperature, "boilers", "minimumTankTemperature"),
  maximumTemperature: getField(ParametersType.Temperature, "boilers", "maximumTankTemperature"),
};
