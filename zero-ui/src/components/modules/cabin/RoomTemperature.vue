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
    <section>
      <span class="inline-flex flex-col items-center justify-center">
        <span
          id="actualTemperature"
          class="font-headers text-5xl font-bold lg:text-7xl md:portrait:text-7xl"
          >{{ actualTemperature !== undefined ? actualTemperature : "-" }}</span
        >
        <label class="text-md text-muted-foreground font-extralight">{{
          t("labels.inside")
        }}</label>
      </span>
      <sup
        v-if="actualTemperature !== undefined"
        class="font-headers text-3xl font-extralight lg:text-5xl md:portrait:text-5xl"
        >&deg;</sup
      >
    </section>

    <section>
      <span class="inline-flex flex-col items-center justify-center">
        <span
          id="outsideTemperature"
          class="font-headers text-5xl font-bold lg:text-7xl md:portrait:text-7xl"
          >33</span
        >
        <label class="text-md text-muted-foreground font-extralight">{{
          t("labels.outside")
        }}</label>
      </span>
      <sup class="font-headers text-3xl font-extralight lg:text-5xl md:portrait:text-5xl"
        >&deg;</sup
      >
    </section>
  </article>
</template>
