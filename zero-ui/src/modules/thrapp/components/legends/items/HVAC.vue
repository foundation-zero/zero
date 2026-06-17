<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import HVACInstance from "../../../mimics/instances/HVACInstance.vue";
import { BOILERS_MIMIC_DATA } from "../../../mimics/modules/boilers/data";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.hvac");
const assets = BOILERS_MIMIC_DATA[MimicComponentType.HVAC];
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HVACInstance
        :force-height="false"
        tag-id="41001001"
        v-bind="assets['41001001']"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
