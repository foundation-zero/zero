import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { ControlStatus } from "@/modules/thrapp/stores/automation";
import { AmcsControlMode } from "@/modules/thrapp/types/thrs";
import { MODULE_GROUPS } from "./sub-navigation.consts";
import { ControlState, ModuleGroup, ModuleOptionGroup } from "./sub-navigation.types";

/**
 * The groups of the module selector, keeping only the modules for which `isAvailable` holds. A
 * module stays (disabled) when only some of its sub-modules are available; empty groups drop out.
 */
export function getModuleOptionGroups(
  isAvailable: (module: MimicKey) => boolean,
  groups: ModuleGroup[] = MODULE_GROUPS,
): ModuleOptionGroup[] {
  return groups
    .map(({ key, modules }) => ({
      key,
      modules: modules
        .map((module) => ({
          key: module.key,
          disabled: !isAvailable(module.key),
          subModules: module.subModules.filter(isAvailable),
        }))
        .filter(({ disabled, subModules }) => !disabled || subModules.length > 0),
    }))
    .filter(({ modules }) => modules.length > 0);
}

/** The module a sub-module belongs to, or `undefined` for a module. */
export function getParentModule(
  module: MimicKey,
  groups: ModuleGroup[] = MODULE_GROUPS,
): MimicKey | undefined {
  return groups
    .flatMap(({ modules }) => modules)
    .find(({ subModules }) => subModules.includes(module))?.key;
}

/** The module whose automation controls the given module or sub-module. */
export function getControlModule(module: MimicKey): keyof ThrsModules {
  return (getParentModule(module) ?? module) as keyof ThrsModules;
}

/** How the module is controlled, or `undefined` while its status is unknown. */
export function getControlState(
  control: ControlStatus | undefined,
  module: keyof ThrsModules | undefined,
): ControlState | undefined {
  const status = module && control?.modules?.[module as keyof ControlStatus["modules"]];
  if (!status?.sensorValues) {
    return undefined;
  }

  if (status.sensorValues.mode?.mode.value !== AmcsControlMode.External) {
    return "advisoryDisabled";
  }

  return status.controlMode?.automatic ? "automatic" : "manual";
}
