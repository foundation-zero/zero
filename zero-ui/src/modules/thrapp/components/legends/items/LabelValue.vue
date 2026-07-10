<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import Label from "@/modules/thrapp/mimics/components/label/Label.vue";
import { useI18n } from "vue-i18n";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const { t } = useI18n();
const tLegend = tScoped("thrapp.legends.labelValue");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <Label
        class="bg-[#BDBDBD]/10"
        height="40"
      >
        <template #value>
          68
          <span>{{ t("units.celsius") }}</span>
        </template>
      </Label>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ tLegend("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
