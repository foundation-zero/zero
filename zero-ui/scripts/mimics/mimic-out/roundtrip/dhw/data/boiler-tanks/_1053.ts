import { ControllerStateComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank1State",
  },
  controls: {},
  controllerState: {
    controller: getField(ControllerStateComponentType.DhwTanksController, "dhw", "dhwTanksController"),
  },
  parameters: {
    enabled: getField(ParametersType.Enabled, "dhw", "tank1Enabled"),
    maximumLevel: getField(ParametersType.Level, "dhw", "maximumTankLevel"),
    maximumTemperature: getField(ParametersType.Temperature, "dhw", "maximumTankTemperature"),
    minimumLevel: getField(ParametersType.Level, "dhw", "minimumTankLevel"),
    minimumTemperature: getField(ParametersType.Temperature, "dhw", "minimumTankTemperature"),
  },
  source: getCustomField("dhw", {
      title: "Tank 1",
      yardTag: "1053",
      technicalName: "hot-water-tank-1",
    }),
  sensors: {
    boostingSupply: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingReturn"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Outlet"),
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Inlet"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank1"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Hot water tank",
    });
  },
});
