<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { BypassArea } from "../../../components/bypass-area";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const { t } = useI18n();
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.Bypasses">
    <BypassArea
      x="592"
      y="320"
      :width="310"
      :height="72"
    >
      {{ t("thrapp.mimics.sections.bypassA") }}
    </BypassArea>

    <BypassArea
      x="310"
      y="290"
      :width="60"
      :height="273"
    >
      {{ t("thrapp.mimics.sections.bypassB") }}
    </BypassArea>
  </LayerFilter>
</template>
