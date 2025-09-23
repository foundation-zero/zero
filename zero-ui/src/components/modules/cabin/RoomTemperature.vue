<script setup lang="ts">
import { Room } from "@/@types";
import { TemperatureDisplay } from "@/components/ui/shared/temperature-display";
import { extractActualTemperature } from "@/lib/utils";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
const props = defineProps<{ room: Room }>();

const actualTemperature = computed(() => extractActualTemperature(props.room));

const { t } = useI18n();
</script>

<template>
  <section class="flex flex-col items-center gap-6">
    <TemperatureDisplay
      v-if="actualTemperature !== undefined"
      id="actualTemperature"
      :value="actualTemperature"
    />
    <span
      v-else
      class="font-headers font-bold"
      >-</span
    >

    <div class="text-muted-foreground text-r5xs">
      <label class="mr-1.5 font-extralight">{{ t("labels.outside") }}</label>
      <span
        id="outsideTemperature"
        class="font-bold"
        >33</span
      >
      <sup class="font-headers text-rxs font-extralight">&deg;</sup>
    </div>
  </section>
</template>
