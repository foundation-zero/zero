<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import CheckValve from "@/modules/heat/mimics/components/check-valve/CheckValve.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("heat.legends.checkValves");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <CheckValve />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
