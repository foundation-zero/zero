import { ControllerStateComponentType, ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank2State",
  },
  controls: {},
  controllerState: {
    controller: getField(ControllerStateComponentType.DhwTanksController, "dhw", "dhwTanksController"),
  },
  parameters: {
    enabled: getField(ParametersType.Enabled, "dhw", "tank2Enabled"),
    maximumLevel: getField(ParametersType.Level, "dhw", "maximumTankLevel"),
    maximumTemperature: getField(ParametersType.Temperature, "dhw", "maximumTankTemperature"),
    minimumLevel: getField(ParametersType.Level, "dhw", "minimumTankLevel"),
    minimumTemperature: getField(ParametersType.Temperature, "dhw", "minimumTankTemperature"),
  },
  source: getCustomField("dhw", {
      title: "Tank 2",
      yardTag: "1054",
      technicalName: "hot-water-tank-2",
    }),
  sensors: {
    boostingSupply: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Outlet"),
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank2"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Inlet"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank2"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      componentType: "Hot water tank",
    });
  },
});
