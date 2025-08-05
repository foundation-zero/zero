<script setup lang="ts">
import { Room } from "@/@types";
import { extractActualTemperature } from "@/lib/utils";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
const props = defineProps<{ room: Room }>();

const actualTemperature = computed(() => extractActualTemperature(props.room));

const { t } = useI18n();
</script>

<template>
  <article class="flex w-100 items-center justify-around">
    <div>
      <span class="inline-flex flex-col items-center justify-center">
        <span
          id="actualTemperature"
          class="text-5xl font-bold lg:text-7xl md:portrait:text-7xl"
          >{{ actualTemperature !== undefined ? actualTemperature : "-" }}</span
        >
        <span class="text-md font-extralight">{{ t("labels.inside") }}</span>
      </span>
      <sup
        v-if="actualTemperature !== undefined"
        class="text-3xl font-extralight lg:text-5xl md:portrait:text-5xl"
        >&deg;</sup
      >
    </div>

    <div>
      <span class="inline-flex flex-col items-center justify-center">
        <span
          id="outsideTemperature"
          class="text-5xl font-bold lg:text-7xl md:portrait:text-7xl"
          >33</span
        >
        <span class="text-md font-extralight">{{ t("labels.outside") }}</span>
      </span>
      <sup class="text-3xl font-extralight lg:text-5xl md:portrait:text-5xl">&deg;</sup>
    </div>
  </article>
</template>
