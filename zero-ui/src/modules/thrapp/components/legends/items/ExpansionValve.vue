<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import ExpansionValve from "@/modules/thrapp/mimics/components/expansion-valve/ExpansionValve.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.expansionValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <ExpansionValve />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
