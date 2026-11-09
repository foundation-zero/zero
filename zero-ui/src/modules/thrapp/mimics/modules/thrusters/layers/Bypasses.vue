<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { BypassArea } from "../../../components/bypass-area";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const { t } = useI18n();
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.SupportComponents">
    <BypassArea
      x="1018"
      y="67"
      :width="172"
      :height="132"
    >
      {{ t("thrapp.mimics.sections.supportComponents") }}
    </BypassArea>
  </LayerFilter>
</template>
