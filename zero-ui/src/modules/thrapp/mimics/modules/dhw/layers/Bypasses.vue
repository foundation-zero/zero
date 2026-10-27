<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { BypassArea } from "../../../components/bypass-area";

const { t } = useI18n();
</script>

<template>
  <g>
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
  </g>
</template>
