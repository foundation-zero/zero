<script setup lang="ts">
import { valueAsArray, valueWithValidation } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { List, ListItem, ListRoot } from "@components/shadcn/list";
import { HeavySlider } from "@components/shared/heavy-slider";
import RoomTemperature from "@modules/cabin/RoomTemperature.vue";
import { computed, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
const MIN_VALUE = 18;

const { currentRoom, hasPendingRequests } = toRefs(useRoomStore());
const { setTemperatureSetpoint } = useRoomStore();
const { t } = useI18n();
const { breakpoints } = useUIStore();

const temperature = ref(currentRoom.value.temperatureSetpoint);

watch(currentRoom, (room) => {
  temperature.value = room.temperatureSetpoint;
});

const value = valueAsArray(valueWithValidation(temperature, (val) => val >= MIN_VALUE));
const isOff = computed(() => value.value[0] === MIN_VALUE);

const commit = () => setTemperatureSetpoint(temperature.value);
</script>

<template>
  <section
    class="flex grow flex-col items-center justify-center max-md:pb-[64px] md:pb-[32px]"
    :class="{ container: !breakpoints.touch, 'w-full px-4 md:px-6': breakpoints.touch }"
  >
    <RoomTemperature
      class="mb-8 w-full"
      :room="currentRoom"
    />

    <div class="flex w-full flex-wrap justify-center">
      <ListRoot class="w-full landscape:max-w-[800px]">
        <List
          orientation="horizontal"
          :size="1"
        >
          <ListItem class="flex-col gap-2">
            <span class="text-lg font-medium">{{ t("labels.airconditioning.long") }}</span>
            <HeavySlider
              v-model:model-value="value"
              class="aspect-[1/2] !h-[40svh] !w-auto"
              :max="24"
              :min="17"
              :min-steps-between-thumbs="3"
              :class="{ 'opacity-70': isOff, disabled: hasPendingRequests }"
              :step="1"
              @click.stop.prevent="commit()"
              @touchend.stop.prevent="commit()"
            />

            <div class="mt-6 flex flex-col items-center justify-center">
              <div
                class="relative inline-flex items-end"
                data-testid="temperatureSetpoint"
              >
                <span class="text-3xl font-bold uppercase md:text-5xl">
                  <span>{{ !isOff ? Math.floor(value[0]) : "Off" }}</span>
                </span>
                <span
                  v-if="!isOff"
                  class="ml-0.5 text-sm font-light max-md:mb-[2.5px] md:text-2xl"
                >
                  {{ Math.round((value[0] % 1) * 10) }}
                </span>
                <sup
                  v-show="!isOff"
                  class="absolute -top-1 right-0 pt-1 text-2xl font-light max-md:mt-[-2px] md:-top-1.5 md:mr-[1.5px] md:text-3xl"
                  >&deg;</sup
                >
              </div>
              <span
                data-testid="temperatureSetpointLabel"
                class="text-xs font-extralight md:text-base"
                :class="{ invisible: isOff }"
                >{{ t("labels.setTo") }}</span
              >
            </div>
          </ListItem>
        </List>
      </ListRoot>
    </div>
  </section>
</template>
