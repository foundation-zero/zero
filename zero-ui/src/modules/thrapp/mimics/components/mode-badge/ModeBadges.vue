<script setup lang="ts">
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
import { computed, toRefs } from "vue";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from ".";

const props = withDefaults(defineProps<{ module?: keyof ThrsModules; size: ModeBadgeSize }>(), {});

const t = tScoped("thrapp.mimics.modeBadge");

const modes = computed(() => {
  if (!props.module) {
    return [];
  }
  const { control } = toRefs(useAutomationStore());

  const automaticMode = control.value?.modules?.[props.module]?.controlMode?.automaticMode;
  const advisoryEnabled =
    control.value?.modules?.[props.module]?.sensorValues?.mode?.mode.value ===
    AmcsControlMode.External;

  if (!advisoryEnabled) {
    return [{ mode: ModeBadgeMode.AdvisoryOff }];
  } else if (!automaticMode) {
    return [{ mode: ModeBadgeMode.ManualControl }];
  } else if (props.module === "pvt") {
    const pvtMode = automaticMode as PvtAutomaticMode;
    const MODES: Record<PvtMode, ModeBadgeMode> = {
      [PvtMode.Idle]: ModeBadgeMode.Idle,
      [PvtMode.Recovery]: ModeBadgeMode.Using,
    };

    return [
      { mode: MODES[pvtMode.aft.mode], label: t(`modes.pvt.${pvtMode.aft.mode}`) },
      {
        mode: MODES[pvtMode.fwd.mode],
        label: t(`modes.pvt.${pvtMode.fwd.mode}`),
      },
      {
        mode: MODES[pvtMode.owners.mode],
        label: t(`modes.pvt.${pvtMode.owners.mode}`),
      },
    ];
  } else if (props.module === "pcm") {
    const pcmMode = automaticMode as PcmAutomaticMode;
    const MODES: Record<string, ModeBadgeMode> = {
      idle: ModeBadgeMode.Idle,
      supplying: ModeBadgeMode.Using,
      boosting: ModeBadgeMode.BoostingLow,
      charging: ModeBadgeMode.Boosting,
    };

    return [{ mode: MODES[pcmMode.mode], label: t(`modes.pcm.${pcmMode.mode}`) }];
  } else if (props.module === "dhw") {
    const dhwMode = automaticMode as DhwAutomaticMode;

    const BOOSTING_MODES: Record<string, ModeBadgeMode> = {
      idle: ModeBadgeMode.Active,
      boosting_low_temperature: ModeBadgeMode.BoostingLow,
      boosting_high_temperature: ModeBadgeMode.Boosting,
      boosting_heatpump: ModeBadgeMode.BoostingHigh,
    };

    const FILLING_MODES: Record<string, ModeBadgeMode> = {
      idle: ModeBadgeMode.Idle,
      filling: ModeBadgeMode.Filling,
    };

    return [
      { mode: BOOSTING_MODES[dhwMode.boostingMode], label: t(`modes.dhw.${dhwMode.boostingMode}`) },
      { mode: FILLING_MODES[dhwMode.fillingMode], label: t(`modes.dhw.${dhwMode.fillingMode}`) },
    ];
  } else if (props.module === "thrusters") {
    const thrustersMode = automaticMode as ThrustersAutomaticMode;
    const MODES: Record<string, ModeBadgeMode> = {
      idle: ModeBadgeMode.Idle,
      recovery: ModeBadgeMode.Using,
      cooling: ModeBadgeMode.Cooling,
      cooldown: ModeBadgeMode.CoolingLow,
    };
    return [{ mode: MODES[thrustersMode.mode], label: t(`modes.thrusters.${thrustersMode.mode}`) }];
  } else {
    return [{ mode: ModeBadgeMode.Active, label: t(`modes.${props.module}`, automaticMode) }];
  }
});
</script>

<template>
  <ModeBadge
    v-for="(data, index) in modes"
    :key="index"
    v-bind="data"
    :size="size"
  />
</template>
