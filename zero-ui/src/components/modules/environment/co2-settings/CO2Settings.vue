<script setup lang="ts">
import { Button } from "@/components/ui/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@/components/ui/shadcn/number-field";
import { CO2_SETPOINT_RANGE } from "@/lib/consts";
import { isCO2Control, updateSetpointWhenControlsHaveChanged } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { ResponsivePopup } from "@components/shared/responsive-dialog";

import { Settings } from "lucide-vue-next";
import { computed, ref, toRefs } from "vue";
import { useI18n } from "vue-i18n";

const store = useRoomStore();
const { allControls, rooms } = toRefs(store);

const roomsWithCO2Control = computed(() =>
  rooms.value.filter((room) => room.roomsControls.some(isCO2Control)),
);

const controls = computed(() => allControls.value.filter(isCO2Control));

const { t } = useI18n();

const value = ref(controls.value?.[0]?.value ?? CO2_SETPOINT_RANGE[0]);

updateSetpointWhenControlsHaveChanged(value, controls);

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
