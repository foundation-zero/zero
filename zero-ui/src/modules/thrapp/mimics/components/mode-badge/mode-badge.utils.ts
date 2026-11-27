import { tScoped } from "@/modules/common/lib/utils";
import { isControlledModule, ThrsModules } from "@/modules/thrapp/lib/consts";
import { DcConverterGroup, PvtGroup } from "@/modules/thrapp/state/state.types";
import {
  ControlStatus,
  DcAutomaticMode,
  DhwAutomaticMode,
  DrivesAutomaticMode,
  PcmAutomaticMode,
  PvtAutomaticMode,
  ThrustersAutomaticMode,
  useAutomationStore,
} from "@/modules/thrapp/stores/automation";
import { AmcsMode, DcMode, PvtMode } from "@/modules/thrapp/types/thrs";
import { computed, MaybeRef, unref } from "vue";
import { NamedValue } from "vue-i18n";
import { ModeBadgeMode } from "./mode-badge.consts";
import { ModeTarget, ModuleModeBadge } from "./mode-badge.types";

/** Translates a key relative to `thrapp.mimics.modeBadge`. */
type Translate = (key: string, values?: NamedValue) => string;

// Modules that control several targets get one badge per target, labelled with its prefix.
const PVT_TARGETS: PvtGroup[] = ["fwd", "aft", "owners"];
const DC_TARGETS: DcConverterGroup[] = ["brightloopsAft", "brightloopsFwd", "ugrids"];
const MODULE_TARGETS: Partial<Record<keyof ThrsModules, ModeTarget[]>> = {
  pvt: PVT_TARGETS,
  dc: DC_TARGETS,
};

const PVT_MODES: Record<PvtMode, ModeBadgeMode> = {
  [PvtMode.Idle]: ModeBadgeMode.Idle,
  [PvtMode.Warmup]: ModeBadgeMode.BoostingLow,
  [PvtMode.Recovery]: ModeBadgeMode.Using,
};

const DC_MODES: Record<DcMode, ModeBadgeMode> = {
  [DcMode.Idle]: ModeBadgeMode.Idle,
  [DcMode.Recovery]: ModeBadgeMode.Using,
};

const DRIVES_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  propulsion: ModeBadgeMode.Active,
  shorepower: ModeBadgeMode.Active,
};

const PCM_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  supplying: ModeBadgeMode.Using,
  boosting: ModeBadgeMode.BoostingLow,
  charging: ModeBadgeMode.Boosting,
};

const DHW_BOOSTING_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  boosting_low_temperature: ModeBadgeMode.BoostingLow,
  boosting_high_temperature: ModeBadgeMode.Boosting,
  boosting_heatpump: ModeBadgeMode.BoostingHigh,
};

const DHW_FILLING_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  filling: ModeBadgeMode.Filling,
};

const THRUSTERS_MODES: Record<string, ModeBadgeMode> = {
  idle: ModeBadgeMode.Idle,
  warmup: ModeBadgeMode.BoostingLow,
  recovery: ModeBadgeMode.Using,
  cooling: ModeBadgeMode.Cooling,
  cooldown: ModeBadgeMode.CoolingLow,
};

const AMCS_MODES = [AmcsMode.Local, AmcsMode.Manual, AmcsMode.Auto];

/**
 * The mode badges of a module: one per target of its automatic mode, or the reason it is not
 * under control (AMCS mode, or one "Manual control" badge per target). A module without a
 * controller has no modes.
 */
export function getModuleModes(
  module: keyof ThrsModules,
  control: ControlStatus | undefined,
  t: Translate,
  targets?: ModeTarget[],
): ModuleModeBadge[] {
  if (!isControlledModule(module)) {
    return [];
  }

  const status = control?.modules?.[module as keyof ControlStatus["modules"]];
  const automaticMode = status?.controlMode?.automaticMode;
  const amcsMode = status?.sensorValues?.mode?.mode.value;

  // Only the requested targets of a multi-target module, e.g. the PVT groups of one sub-mimic.
  const isShown = (target: ModeTarget) => !targets || targets.includes(target);
  const shownTargets = (MODULE_TARGETS[module] ?? []).filter(isShown);
  // A prefix tells targets apart, so a single target is shown without it.
  const prefixed = (target: ModeTarget, label: string) =>
    shownTargets.length > 1
      ? t("prefixed", { prefix: t(`prefixes.${module}.${target}`), label })
      : label;

  if (amcsMode !== AmcsMode.External) {
    const label = amcsMode && AMCS_MODES.includes(amcsMode) ? t(`amcs.${amcsMode}`) : undefined;
    return [{ mode: ModeBadgeMode.AdvisoryOff, label }];
  }

  // Unknown until the control mode is loaded; never announce manual control before that.
  if (!status?.controlMode) {
    return [];
  }

  if (!status.controlMode.automatic) {
    const label = t(`modes.${ModeBadgeMode.ManualControl}`);
    return MODULE_TARGETS[module]
      ? shownTargets.map((target) => ({
          mode: ModeBadgeMode.ManualControl,
          label: prefixed(target, label),
        }))
      : [{ mode: ModeBadgeMode.ManualControl, label }];
  }

  if (!automaticMode) {
    return [];
  }

  switch (module) {
    case "pvt": {
      const pvtMode = automaticMode as PvtAutomaticMode;
      return PVT_TARGETS.filter(isShown).map((target) => {
        const { mode } = pvtMode[target];
        return { mode: PVT_MODES[mode], label: prefixed(target, t(`modes.pvt.${mode}`)) };
      });
    }
    case "dc": {
      const dcMode = automaticMode as DcAutomaticMode;
      return DC_TARGETS.filter(isShown).map((target) => {
        const { mode } = dcMode[target];
        return { mode: DC_MODES[mode], label: prefixed(target, t(`modes.dc.${mode}`)) };
      });
    }
    case "drives": {
      const { mode } = automaticMode as DrivesAutomaticMode;
      return [{ mode: DRIVES_MODES[mode], label: t(`modes.drives.${mode}`) }];
    }
    case "pcm": {
      const { mode } = automaticMode as PcmAutomaticMode;
      return [{ mode: PCM_MODES[mode], label: t(`modes.pcm.${mode}`) }];
    }
    case "dhw": {
      const { boostingMode, fillingMode } = automaticMode as DhwAutomaticMode;
      return [
        {
          mode: DHW_BOOSTING_MODES[boostingMode],
          label: t(`modes.dhw.boosting.${boostingMode}`),
        },
        {
          mode: DHW_FILLING_MODES[fillingMode],
          label: t(`modes.dhw.filling.${fillingMode}`),
        },
      ];
    }
    case "thrusters": {
      const { mode } = automaticMode as ThrustersAutomaticMode;
      return [{ mode: THRUSTERS_MODES[mode], label: t(`modes.thrusters.${mode}`) }];
    }
    default:
      return [
        { mode: ModeBadgeMode.Active, label: t(`modes.${module}`, automaticMode as NamedValue) },
      ];
  }
}

export const useModuleMode = (
  moduleRef?: MaybeRef<keyof ThrsModules | undefined>,
  targetsRef?: MaybeRef<ModeTarget[] | undefined>,
) => {
  const t = tScoped("thrapp.mimics.modeBadge");
  const automation = useAutomationStore();

  return computed(() => {
    const module = unref(moduleRef);
    return module ? getModuleModes(module, automation.control, t, unref(targetsRef)) : [];
  });
};
