<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { BypassArea } from "@/modules/thrapp/mimics/components/bypass-area";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.sectionArea");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <BypassArea
        :width="50"
        :height="40"
      >
        {{ t("assetTitle") }}
      </BypassArea>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
