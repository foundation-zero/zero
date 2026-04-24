<script setup lang="ts">
import RoomTemperature from "@/modules/domestic/cabin/components/RoomTemperature.vue";
import { HeavySlider } from "@/modules/domestic/cabin/components/ui/heavy-slider";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { TemperatureDisplay } from "@common/components/temperature-display";
import { valueAsArray, valueWithValidation } from "@common/lib/utils";
import { useUIStore } from "@common/stores/ui";
import { computed, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
const MIN_VALUE = 18;

const { currentRoom, hasPendingRequests } = toRefs(useRoomStore());

const { setTemperatureSetpoint } = useRoomStore();
const { t } = useI18n();
const { breakpoints } = useUIStore();

const hasTemperatureControl = computed(() => !!currentRoom.value.airConditioning);
const temperature = ref(currentRoom.value.airConditioning?.temperatureSetpoint ?? 0);

watch(currentRoom, (room) => {
  temperature.value = room.airConditioning?.temperatureSetpoint ?? 0;
});

const value = valueAsArray(valueWithValidation(temperature, (val) => val >= MIN_VALUE));
const isOff = computed(() => value.value[0] === MIN_VALUE);

const commit = async () => {
  await setTemperatureSetpoint(temperature.value);

  if (!hasPendingRequests.value) return;

  watch(
    hasPendingRequests,
    () => (temperature.value = currentRoom.value.airConditioning?.temperatureSetpoint ?? 0),
    { once: true },
  );
};
</script>

<template>
  <section
    class="mt-4 flex grow flex-col items-center justify-around max-md:pb-24 md:pb-8"
    :class="{ container: !breakpoints.touch, 'w-full px-4 md:px-6': breakpoints.touch }"
  >
    <RoomTemperature
      class="w-full max-md:text-6xl md:text-7xl xl:text-8xl"
      :room="currentRoom"
    />

    <div class="my-4 h-[40svh] max-w-2xs">
      <HeavySlider
        v-model:model-value="value"
        class="aspect-1/2"
        :max="24"
        :min="17"
        :min-steps-between-thumbs="3"
        :class="{ 'opacity-70': isOff, disabled: hasPendingRequests }"
        :step="1"
        @click.stop.prevent="commit()"
        @touchend.stop.prevent="commit()"
      />
    </div>

    <div class="flex flex-col items-center gap-4 max-md:text-5xl md:text-6xl xl:text-7xl">
      <TemperatureDisplay
        v-if="hasTemperatureControl && !isOff"
        data-testid="temperatureSetpoint"
        class="text-foreground"
        :value="value[0]"
        :off="isOff"
        :has-temperature-control="hasTemperatureControl"
      />
      <span
        v-else
        class="font-headers font-bold uppercase"
      >
        {{ isOff ? t("labels.off") : "-" }}
      </span>

      <label
        data-testid="temperatureSetpointLabel"
        class="text-muted-foreground text-r5xs font-extralight"
        :class="{ invisible: isOff }"
        >{{ t("labels.setTo") }}</label
      >
    </div>
  </section>
</template>
