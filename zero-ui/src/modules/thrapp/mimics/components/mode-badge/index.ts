import { tScoped } from "@/modules/common/lib/utils";
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import {
  DhwAutomaticMode,
  PcmAutomaticMode,
  PvtAutomaticMode,
  ThrustersAutomaticMode,
  useAutomationStore,
} from "@/modules/thrsim/stores/automation";
import { AmcsControlMode, PvtMode } from "@/modules/thrsim/types";
import { computed, MaybeRef, unref } from "vue";

export { default as ModeBadge } from "./ModeBadge.vue";
export { default as ModeBadges } from "./ModeBadges.vue";

export const enum ModeBadgeMode {
  Idle = "Idle",

  Active = "Active",
  Using = "Using",

  CoolingLow = "CoolingLow",
  Cooling = "Cooling",
  CoolingHigh = "CoolingHigh",

  ManualControl = "ManualControl",
  AdvisoryOff = "AdvisoryOff",
  Disabled = "Disabled",

  BoostingLow = "BoostingLow",
  Boosting = "Boosting",
  BoostingHigh = "BoostingHigh",

  FillingLow = "FillingLow",
  Filling = "Filling",
}

export const enum ModeBadgeSize {
  Asset = "asset",
  Circuit = "circuit",
  Tank = "tank",
}

export const SIZE_ATTRIBUTES: Record<ModeBadgeSize, string> = {
  [ModeBadgeSize.Asset]: "rounded-lg py-0.5 text-xs",
  [ModeBadgeSize.Tank]: "rounded-lg py-0.5 text-xs",
  [ModeBadgeSize.Circuit]: "rounded-xl py-1 text-sm",
};

export const MODE_COLORS: Record<ModeBadgeMode, string> = {
  [ModeBadgeMode.Idle]: "var(--muted-foreground)",
  [ModeBadgeMode.Active]: "var(--constructive)",
  [ModeBadgeMode.Using]: "var(--flows-use-medium)",
  [ModeBadgeMode.CoolingLow]: "var(--cooling-low)",
  [ModeBadgeMode.Cooling]: "var(--cooling-medium)",
  [ModeBadgeMode.CoolingHigh]: "var(--cooling-high)",
  [ModeBadgeMode.BoostingLow]: "var(--heating-low)",
  [ModeBadgeMode.Boosting]: "var(--heating-medium)",
  [ModeBadgeMode.BoostingHigh]: "var(--heating-high)",
  [ModeBadgeMode.FillingLow]: "var(--flows-fill-low)",
  [ModeBadgeMode.Filling]: "var(--flows-fill-medium)",
  [ModeBadgeMode.ManualControl]: "var(--warning)",
  [ModeBadgeMode.AdvisoryOff]: "var(--destructive)",
  [ModeBadgeMode.Disabled]: "var(--destructive-muted)",
};

export const useModuleMode = (moduleRef?: MaybeRef<keyof ThrsModules | undefined>) => {
  const t = tScoped("thrapp.mimics.modeBadge");

  return computed(() => {
    const module = unref(moduleRef);

    if (!module) {
      return [];
    }

    const { control } = useAutomationStore();

    const automaticMode = control?.modules?.[module]?.controlMode?.automaticMode;
    const advisoryEnabled =
      control?.modules?.[module]?.sensorValues?.mode?.mode.value === AmcsControlMode.External;

    if (!advisoryEnabled) {
      return [{ mode: ModeBadgeMode.AdvisoryOff }];
    } else if (!automaticMode) {
      return [{ mode: ModeBadgeMode.ManualControl }];
    } else if (module === "pvt") {
      const pvtMode = automaticMode as PvtAutomaticMode;
      const MODES: Record<PvtMode, ModeBadgeMode> = {
        [PvtMode.Idle]: ModeBadgeMode.Idle,
        [PvtMode.Recovery]: ModeBadgeMode.Using,
      };

      return [
        { mode: MODES[pvtMode.aft.mode], label: t(`modes.pvt.${pvtMode.aft.mode}`, { count: 0 }) },
        {
          mode: MODES[pvtMode.fwd.mode],
          label: t(`modes.pvt.${pvtMode.fwd.mode}`, { count: 1 }),
        },
        {
          mode: MODES[pvtMode.owners.mode],
          label: t(`modes.pvt.${pvtMode.owners.mode}`, { count: 2 }),
        },
      ];
    } else if (module === "pcm") {
      const pcmMode = automaticMode as PcmAutomaticMode;
      const MODES: Record<string, ModeBadgeMode> = {
        idle: ModeBadgeMode.Idle,
        supplying: ModeBadgeMode.Using,
        boosting: ModeBadgeMode.BoostingLow,
        charging: ModeBadgeMode.Boosting,
      };

      return [{ mode: MODES[pcmMode.mode], label: t(`modes.pcm.${pcmMode.mode}`) }];
    } else if (module === "dhw") {
      const dhwMode = automaticMode as DhwAutomaticMode;

      const BOOSTING_MODES: Record<string, ModeBadgeMode> = {
        idle: ModeBadgeMode.Idle,
        boosting_low_temperature: ModeBadgeMode.BoostingLow,
        boosting_high_temperature: ModeBadgeMode.Boosting,
        boosting_heatpump: ModeBadgeMode.BoostingHigh,
      };

      const FILLING_MODES: Record<string, ModeBadgeMode> = {
        idle: ModeBadgeMode.Idle,
        filling: ModeBadgeMode.Filling,
      };

      return [
        {
          mode: BOOSTING_MODES[dhwMode.boostingMode],
          label: t(`modes.dhw.boosting.${dhwMode.boostingMode}`),
        },
        {
          mode: FILLING_MODES[dhwMode.fillingMode],
          label: t(`modes.dhw.filling.${dhwMode.fillingMode}`),
        },
      ];
    } else if (module === "thrusters") {
      const thrustersMode = automaticMode as ThrustersAutomaticMode;
      const MODES: Record<string, ModeBadgeMode> = {
        idle: ModeBadgeMode.Idle,
        recovery: ModeBadgeMode.Using,
        cooling: ModeBadgeMode.Cooling,
        cooldown: ModeBadgeMode.CoolingLow,
      };
      return [
        { mode: MODES[thrustersMode.mode], label: t(`modes.thrusters.${thrustersMode.mode}`) },
      ];
    } else {
      return [{ mode: ModeBadgeMode.Active, label: t(`modes.${module}`, automaticMode) }];
    }
  });
};
