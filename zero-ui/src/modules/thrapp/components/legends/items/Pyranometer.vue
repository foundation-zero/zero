<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { PyranoMeter } from "@/modules/thrapp/mimics/components/pyrano-meter";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.pyranometer");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <PyranoMeter />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
