<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../mimics/data";
import HVACInstance from "../../../mimics/instances/HVACInstance.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.hvac");
const hvac = getTooltipContext(MimicComponentType.HVAC)("41001001");
</script>

<template>
  <LegendItem class="min-h-27">
    <LegendItemPreview>
      <HVACInstance
        :force-height="false"
        v-bind="hvac"
      />
    </LegendItemPreview>
    <LegendItemInfo class="gap-2">
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
