<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { QueryLoadCase } from "../types/queries";

defineProps<{ loadCase?: QueryLoadCase | null }>();

const { t } = useI18n();
</script>

<template>
  <p
    v-if="loadCase"
    class="text-muted-foreground text-xs leading-none font-medium whitespace-nowrap"
  >
    {{
      t("loads.components.selectedLoadCase", {
        name: loadCase.name,
        awa: loadCase.awa.toFixed(1),
        aws: loadCase.aws.toFixed(1),
        heel: loadCase.heel.toFixed(1),
        twa: loadCase.twa.toFixed(1),
        tws: loadCase.tws.toFixed(1),
      })
    }}
  </p>
</template>
