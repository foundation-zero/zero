<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils";
import { useI18n } from "vue-i18n";
import { WindCondition, WindConditionLabel, WindConditionValue } from ".";

const { t } = useI18n();

defineProps<{ awa?: number; aws?: number }>();
</script>

<template>
  <div
    class="bg-background flex h-9 min-w-45 items-center justify-center gap-2 rounded-sm px-2 py-1 text-sm font-medium tracking-normal"
  >
    <WindCondition>
      <WindConditionLabel>{{ t("loads.components.awaSelector.short") }}:</WindConditionLabel>
      <WindConditionValue>{{ awa ? formatInt(awa) : 0 }}&deg;</WindConditionValue>
    </WindCondition>
    <WindCondition>
      <WindConditionLabel>{{ t("loads.components.awsSelector.short") }}:</WindConditionLabel>
      <WindConditionValue
        >{{ aws ? formatInt(aws) : 0 }}
        {{ t("loads.components.awsSelector.unit") }}</WindConditionValue
      >
    </WindCondition>
  </div>
</template>
