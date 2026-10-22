<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import AirTrapVessel from "@/modules/thrapp/mimics/components/air-trap-vessel/AirTrapVessel.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.airTrapVessel");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <AirTrapVessel />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
