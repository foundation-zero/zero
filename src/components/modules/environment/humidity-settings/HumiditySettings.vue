<script setup lang="ts">
import { HUMIDITY_SETPOINT_RANGE } from "@/lib/consts";
import {
  isHumidityControl,
  ratioAsPercentage,
  updateSetpointWhenControlsHaveChanged,
} from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { Button } from "@components/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@components/shadcn/number-field";
import { ResponsivePopup } from "@components/shared/responsive-dialog";

import { Settings } from "lucide-vue-next";
import { computed, ref, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const store = useRoomStore();
const { allControls, rooms } = toRefs(store);

const roomsWithHumidityControl = computed(() =>
  rooms.value.filter((room) => room.roomsControls.some(isHumidityControl)),
);

const controls = computed(() => allControls.value.filter(isHumidityControl));

const { t } = useI18n();

const value = ref(controls.value?.[0]?.value ?? HUMIDITY_SETPOINT_RANGE[0]);
const valuePercentage = ratioAsPercentage(value);

updateSetpointWhenControlsHaveChanged(valuePercentage, controls);

const open = ref(false);

const save = () => {
  store.setHumiditySetpoints(
    roomsWithHumidityControl.value.map((c) => c.id),
    valuePercentage.value,
  );
  open.value = false;
};
</script>

<template>
  <ResponsivePopup
    v-model:open="open"
    :title="t('views.humiditySettings.title')"
    :description="t('views.humiditySettings.description')"
  >
    <template #trigger>
      <button><Settings /></button>
    </template>
    <div class="max-md:p-4">
      <NumberField
        id="percent"
        v-model="value"
        class="my-12"
        :default-value="0.55"
        :step="0.01"
        :min="0.35"
        :max="0.7"
        :format-options="{
          style: 'percent',
        }"
      >
        <NumberFieldContent>
          <NumberFieldDecrement /> <NumberFieldInput class="text-xl" /> <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>
      <Button
        class="mt-4 block w-full text-base"
        size="lg"
        @click="save"
        >{{ t("labels.save") }}</Button
      >
    </div>
  </ResponsivePopup>
</template>
