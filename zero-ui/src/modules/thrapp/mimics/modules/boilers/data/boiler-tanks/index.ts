import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";

import { ExtractModuleFields, ParameterFieldDefinitions } from "@/modules/thrapp/types/fields";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import _1053 from "./_1053";
import _1054 from "./_1054";
import _1055 from "./_1055";

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

export const toBoilerTank = toInstance<MimicComponentType.BoilerTank>;

export const BOILER_TANK_DATA = toFieldsMap({
  [MimicComponentType.BoilerTank]: {
    "1053": _1053,
    "1054": _1054,
    "1055": _1055,
  },
});
