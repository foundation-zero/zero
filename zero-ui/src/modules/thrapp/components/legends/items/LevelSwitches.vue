<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import LevelSwitch from "../../../mimics/components/level-switch/LevelSwitch.vue";
import {
  LegendItem,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend/index.ts";

const t = tScoped("thrapp.legends.levelSwitches");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <LevelSwitch />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
