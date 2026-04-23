<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/number-field";
import { CO2_SETPOINT_RANGE } from "@/modules/domestic/lib/consts";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { ResponsivePopup } from "@common/components/responsive-dialog";
import { hasCO2Control, updateSetpointWhenControlsHaveChanged } from "@common/lib/utils";

import { Settings } from "lucide-vue-next";
import { computed, ref, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const store = useRoomStore();
const { rooms } = toRefs(store);

const roomsWithCO2Control = computed(() => rooms.value.filter(hasCO2Control));

const controls = computed(() =>
  roomsWithCO2Control.value.map((room) => room.ventilation).filter((control) => !!control),
);

const { t } = useI18n();

const value = ref(controls.value?.[0]?.co2Setpoint ?? CO2_SETPOINT_RANGE[0]);

updateSetpointWhenControlsHaveChanged(value, controls, "co2Setpoint");

const open = ref(false);

const save = () => {
  store.setCO2Setpoints(
    roomsWithCO2Control.value.map((c) => c.id),
    value.value,
  );
  open.value = false;
};
</script>

<template>
  <ResponsivePopup
    v-model:open="open"
    :title="t('views.co2Settings.title')"
    :description="t('views.co2Settings.description')"
  >
    <template #trigger>
      <button><Settings /></button>
    </template>
    <div class="max-md:p-4">
      <NumberField
        v-model="value"
        class="my-12"
        :default-value="CO2_SETPOINT_RANGE[0]"
        :step="50"
        :min="CO2_SETPOINT_RANGE[0]"
        :max="CO2_SETPOINT_RANGE[1]"
      >
        <NumberFieldContent>
          <NumberFieldDecrement /> <NumberFieldInput class="text-xl" />
          <NumberFieldIncrement />
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
