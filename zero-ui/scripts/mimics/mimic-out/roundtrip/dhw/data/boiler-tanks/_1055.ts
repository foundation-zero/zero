import { ControllerStateComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank3State",
  },
  controls: {},
  controllerState: {
    controller: getField(ControllerStateComponentType.DhwTanksController, "dhw", "dhwTanksController"),
  },
  parameters: {
    enabled: getField(ParametersType.Enabled, "dhw", "tank3Enabled"),
    maximumLevel: getField(ParametersType.Level, "dhw", "maximumTankLevel"),
    maximumTemperature: getField(ParametersType.Temperature, "dhw", "maximumTankTemperature"),
    minimumLevel: getField(ParametersType.Level, "dhw", "minimumTankLevel"),
    minimumTemperature: getField(ParametersType.Temperature, "dhw", "minimumTankTemperature"),
  },
  source: getCustomField("dhw", {
      title: "Tank 3",
      yardTag: "1055",
      technicalName: "hot-water-tank-3",
    }),
  sensors: {
    boostingSupply: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingReturn"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingSupply"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Outlet"),
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank3"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Inlet"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank3"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Hot water tank",
    });
  },
});
