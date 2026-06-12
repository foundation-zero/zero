import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { CustomFieldDefinitions } from "@/modules/thrapp/types/fields";
import { toFieldsMap } from "../..";
import { MimicComponentType } from "../../../../types";
import { getField } from "../../../providers";
import { BOILER_TANK_DATA } from "./boiler-tanks";

const tooltip = (tooltip: Partial<TooltipContent>): TooltipContent => ({
  title: "Switch valve",
  itemName: "2 way valve DN 25",
  ...tooltip,
});

const controller = getField(
  ControlComponentType.BoilersTanksController,
  "boilers",
  "boilersTanksController",
);

type SwitchValveCustom = CustomFieldDefinitions[MimicComponentType.SwitchValve]["tank"];

const tank1: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank][1053].sensors;
  },
  operatorName: "Tank 1 operator",
};

const tank2: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank][1054].sensors;
  },
  operatorName: "Tank 2 operator",
};

const tank3: SwitchValveCustom = {
  controller,
  get operator() {
    return BOILER_TANK_DATA[MimicComponentType.BoilerTank][1055].sensors;
  },
  operatorName: "Tank 3 operator",
};

export const BOILER_SWITCH_VALVE_DATA = toFieldsMap({
  [MimicComponentType.SwitchValve]: {
    "1067-11": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
      },
      custom: { tank: tank1 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
      },
      tooltip: tooltip({
        yardTag: "1067-11",
        technicalName: "boilers-switch-tank-1-fill",
      }),
    },
    "1067-12": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1BoostingReturn"),
      },
      custom: { tank: tank1 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1BoostingReturn"),
      },
      tooltip: tooltip({
        yardTag: "1067-12",
        technicalName: "boilers-switch-tank-1-boosting-return",
      }),
    },
    "1067-14": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1BoostingSupply"),
      },
      custom: { tank: tank1 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1BoostingSupply"),
      },
      tooltip: tooltip({
        yardTag: "1067-14",
        technicalName: "boilers-switch-tank-1-boosting-supply",
      }),
    },
    "1067-13": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
      },
      custom: { tank: tank1 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
      },
      tooltip: tooltip({
        yardTag: "1067-13",
        technicalName: "boilers-switch-tank-1-empty",
      }),
    },
    "1067-07": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
      },
      custom: { tank: tank2 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
      },
      tooltip: tooltip({
        yardTag: "1067-07",
        technicalName: "boilers-switch-tank-2-fill",
      }),
    },
    "1067-08": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2BoostingReturn"),
      },
      custom: { tank: tank2 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2BoostingReturn"),
      },
      tooltip: tooltip({
        yardTag: "1067-08",
        technicalName: "boilers-switch-tank-2-boosting-return",
      }),
    },
    "1067-10": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2BoostingSupply"),
      },
      custom: { tank: tank2 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2BoostingSupply"),
      },
      tooltip: tooltip({
        yardTag: "1067-10",
        technicalName: "boilers-switch-tank-2-boosting-supply",
      }),
    },
    "1067-09": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank2Empty"),
      },
      custom: { tank: tank2 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Empty"),
      },
      tooltip: tooltip({
        yardTag: "1067-09",
        technicalName: "boilers-switch-tank-2-empty",
      }),
    },
    "1067-03": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
      },
      custom: { tank: tank3 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
      },
      tooltip: tooltip({
        yardTag: "1067-03",
        technicalName: "boilers-switch-tank-3-fill",
      }),
    },
    "1067-04": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3BoostingReturn"),
      },
      custom: { tank: tank3 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3BoostingReturn"),
      },
      tooltip: tooltip({
        yardTag: "1067-04",
        technicalName: "boilers-switch-tank-3-boosting-return",
      }),
    },
    "1067-06": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3BoostingSupply"),
      },
      custom: { tank: tank3 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3BoostingSupply"),
      },
      tooltip: tooltip({
        yardTag: "1067-06",
        technicalName: "boilers-switch-tank-3-boosting-supply",
      }),
    },
    "1067-05": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
      },
      custom: { tank: tank3 },
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
      },
      tooltip: tooltip({
        yardTag: "1067-05",
        technicalName: "boilers-switch-tank-3-empty",
      }),
    },
    "1067-17": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
      },
      custom: {},
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchHeatpump"),
      },
      tooltip: tooltip({
        yardTag: "1067-17",
        technicalName: "boilers-switch-heatpump",
      }),
    },
    "1067-16": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchLowTemperature"),
      },
      custom: {},
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchLowTemperature"),
      },
      tooltip: tooltip({
        yardTag: "1067-16",
        technicalName: "boilers-switch-low-temperature",
      }),
    },
    "1067-18": {
      controls: {
        valve: getField(ControlComponentType.Valve, "boilers", "boilersSwitchHighTemperature"),
      },
      custom: {},
      parameters: {},
      sensors: {
        valve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchHighTemperature"),
      },
      tooltip: tooltip({
        yardTag: "1067-18",
        technicalName: "boilers-switch-high-temperature",
      }),
    },
  },
});
