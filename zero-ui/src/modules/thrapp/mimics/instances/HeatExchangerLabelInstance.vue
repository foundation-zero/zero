<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiFireLine } from "@remixicon/vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps, useRandomizedNumber } from ".";
import { Label } from "../components/label";

defineProps<MimicComponentInstanceProps>();

const { t } = useI18n();

const deltaTRaw = useRandomizedNumber(-90, 90);
const powerRaw = useRandomizedNumber(5, 30);

const deltaTSign = computed(() => (deltaTRaw.value >= 0 ? "+" : ""));
const deltaTValue = computed(() => Math.abs(deltaTRaw.value) / 10);
const powerValue = computed(() => powerRaw.value / 10);
</script>

<template>
  <Label
    :x="x"
    :y="y"
    class="w-20"
  >
    {{ tagId }}
    <template #value>
      <div class="flex items-center">
        <span class="text-brand inline-block w-5">{{ t("units.deltaT") }}</span>
        <span>{{ deltaTSign }}</span>
        <AnimatedNumber
          :to="deltaTValue"
          :fraction-digits="1"
        />
        <span>{{ t("units.celsius") }}</span>
      </div>
      <div class="flex items-center">
        <span class="inline-block w-5">
          <RiFireLine class="text-heating-medium inline size-4" />
        </span>
        <span>
          <AnimatedNumber
            :to="powerValue"
            :fraction-digits="1"
          />
          {{ t("units.kilowatt") }}
        </span>
      </div>
    </template>
  </Label>
</template>
