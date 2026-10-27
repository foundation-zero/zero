<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { BypassArea } from "../../../components/bypass-area";

const { t } = useI18n();
</script>

<template>
  <g>
    <BypassArea
      x="1018"
      y="67"
      :width="172"
      :height="181"
    >
      {{ t("thrapp.mimics.sections.supportComponents") }}
    </BypassArea>
  </g>
</template>
