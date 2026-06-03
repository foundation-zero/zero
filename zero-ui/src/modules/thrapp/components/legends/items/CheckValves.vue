<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import CheckValve from "@/modules/thrapp/mimics/components/check-valve/CheckValve.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.checkValves");
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
