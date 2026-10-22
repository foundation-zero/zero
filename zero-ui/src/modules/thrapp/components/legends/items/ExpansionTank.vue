<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import ExpansionTank from "@/modules/thrapp/mimics/components/expansion-tank/ExpansionTank.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.expansionTank");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <ExpansionTank />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
