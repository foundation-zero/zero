import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";

import { ExtractModuleFields, ParameterFieldDefinitions } from "@/modules/thrapp/types/fields";
import { toFieldsMap } from "../..";
import { MimicComponentType } from "../../../../types";
import { getField } from "../../../providers";

const controller = getField(
  ControlComponentType.BoilersTanksController,
  "boilers",
  "boilersTanksController",
);

const boostingSupply = getField(
  SensorComponentType.Temperature,
  "boilers",
  "boilersTemperatureBoostingSupply",
);

type BoilerTankParameters = ExtractModuleFields<
  ParameterFieldDefinitions[MimicComponentType.BoilerTank]
>;

const parameters: BoilerTankParameters = {
  minimumLevel: getField(ParametersType.Level, "boilers", "minimumTankLevel"),
  maximumLevel: getField(ParametersType.Level, "boilers", "maximumTankLevel"),
  minimumTemperature: getField(ParametersType.Temperature, "boilers", "minimumTankTemperature"),
  maximumTemperature: getField(ParametersType.Temperature, "boilers", "maximumTankTemperature"),
};

export const BOILER_TANK_DATA = toFieldsMap({
  [MimicComponentType.BoilerTank]: {
    "1053": {
      custom: {
        tankStateField: "tank1State",
      },
      controls: {
        controller,
      },
      parameters,
      sensors: {
        boostingSupply,
        level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank1"),
        temperature: getField(
          SensorComponentType.Temperature,
          "boilers",
          "boilersTemperatureTank1",
        ),
        boostSupplyValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank1BoostingSupply",
        ),
        boostReturnValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank1BoostingReturn",
        ),
        supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
        dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
      },
      tooltip: {
        title: "Tank 1",
        itemName: "Hot water tank",
        technicalName: "hot-water-tank-1",
        yardTag: "1053",
      },
    },
    "1054": {
      custom: {
        tankStateField: "tank2State",
      },
      controls: {
        controller,
      },
      parameters,
      sensors: {
        boostingSupply,
        level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank2"),
        temperature: getField(
          SensorComponentType.Temperature,
          "boilers",
          "boilersTemperatureTank2",
        ),
        boostSupplyValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank2BoostingSupply",
        ),
        boostReturnValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank2BoostingReturn",
        ),
        supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
        dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Empty"),
      },
      tooltip: {
        title: "Tank 2",
        itemName: "Hot water tank",
        technicalName: "hot-water-tank-2",
        yardTag: "1054",
      },
    },
    "1055": {
      custom: {
        tankStateField: "tank3State",
      },
      controls: {
        controller,
      },
      parameters,
      sensors: {
        boostingSupply,
        level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank3"),
        temperature: getField(
          SensorComponentType.Temperature,
          "boilers",
          "boilersTemperatureTank3",
        ),
        boostSupplyValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank3BoostingSupply",
        ),
        boostReturnValve: getField(
          SensorComponentType.Valve,
          "boilers",
          "boilersSwitchTank3BoostingReturn",
        ),
        supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
        dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
      },
      tooltip: {
        title: "Tank 3",
        itemName: "Hot water tank",
        technicalName: "hot-water-tank-3",
        yardTag: "1055",
      },
    },
  },
});
