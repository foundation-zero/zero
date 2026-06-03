<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import Label from "@/modules/thrapp/mimics/components/label/Label.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.labelTag");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <Label
        class="bg-[#BDBDBD]/10"
        height="28"
        :offset-y="0"
        >{{ t("labelValue") }}</Label
      >
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
