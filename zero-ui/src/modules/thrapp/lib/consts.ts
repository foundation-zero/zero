import { keysOf } from "@/modules/common/lib/utils";
import {
  ControlComponentType,
  ControlFields,
  ControllerStateComponentType,
  ControllerStateFields,
  ModuleDefinition,
  SensorComponentType,
  SensorFields,
} from "@/modules/thrapp/types/thrs";
import { MQTT_GRAPHQL_DEFINITIONS } from "./definitions.generated";

export * from "./consts.types";

export const THRS_YARDTAG_PREFIX_REGEX = /^5000/;

type ModuleDefinitions = Record<string, ModuleDefinition>;

export const toDefinitions = <T extends ModuleDefinitions>(input: T): T => input;

// The modules as the MQTT GraphQL API serves them, generated from the AsyncAPI Specs.
export const DEFINITIONS = toDefinitions(MQTT_GRAPHQL_DEFINITIONS);

export type ThrsDefinitions = typeof DEFINITIONS;

// The modules with a controller: those thrs-control takes parameters for.
export type ControlledModule = {
  [Module in keyof ThrsDefinitions]: keyof ThrsDefinitions[Module]["parameters"] extends never
    ? never
    : Module;
}[keyof ThrsDefinitions];

export const CONTROLLED_MODULES = keysOf(DEFINITIONS).filter(
  (module): module is ControlledModule => Object.keys(DEFINITIONS[module].parameters).length > 0,
);

export const isControlledModule = (module: string): module is ControlledModule =>
  (CONTROLLED_MODULES as string[]).includes(module);

export const CONTROL_FIELDS: ControlFields = {
  [ControlComponentType.Pump]: ["dutypoint", "on"],
  [ControlComponentType.Valve]: ["setpoint"],
  [ControlComponentType.Pcm]: ["on"],
  [ControlComponentType.Heatpump]: ["temperatureSetpoint", "on"],
};

export const CONTROLLER_STATE_FIELDS: ControllerStateFields = {
  [ControllerStateComponentType.DhwTanksController]: [
    "tank1State",
    "tank2State",
    "tank3State",
    "timeToFill",
    "timeToHot",
  ],
  [ControllerStateComponentType.PIDController]: [
    "target",
    "measurement",
    "output",
    "error",
    "enabled",
    "tuning",
    "components",
  ],
};

export const SENSOR_FIELDS: SensorFields = {
  [SensorComponentType.Pump]: ["flow", "speed", "opTime"],
  [SensorComponentType.Valve]: ["positionRel"],
  [SensorComponentType.Pressure]: ["pressure"],
  [SensorComponentType.Temperature]: ["temperature"],
  [SensorComponentType.Thruster]: ["active"],
  [SensorComponentType.Pcs]: ["mode"],
  [SensorComponentType.Flow]: ["flow", "temperature", "quantity"],
  [SensorComponentType.Level]: ["level"],
  [SensorComponentType.LevelSwitch]: ["empty"],
};
