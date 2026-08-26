<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import HVACInstance from "../../../mimics/instances/HVACInstance.vue";
import { DHW_MIMIC_DATA } from "../../../mimics/modules/dhw/data/index.ts";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.hvac");
const assets = DHW_MIMIC_DATA[MimicComponentType.HVAC];
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HVACInstance
        :force-height="false"
        v-bind="assets['41001001']"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
