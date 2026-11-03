<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils";
import { CONTROL_FIELDS, DEFINITIONS, SENSOR_FIELDS } from "@/modules/thrapp/lib/consts";
import { inject, Ref, toRef, watchEffect } from "vue";
import { useI18n } from "vue-i18n";
import {
  FieldCurrent,
  FieldHeader,
  FieldsFilter,
  FieldsValues,
  FieldsValuesEmpty,
} from "../components/fields-values";
import { MONITORING_PAGE_QUERIES } from "@/modules/thrapp/lib/queries.consts";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { storeToRefs } from "pinia";

const { t } = useI18n();

const data = toRef(useThrsHistory(), "data");
const SENSOR_VALUES = Array.from(new Set(Object.values(SENSOR_FIELDS).flat()));
const CONTROL_VALUES = Array.from(new Set(Object.values(CONTROL_FIELDS).flat()));
const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;

const { activeQuery } = storeToRefs(useThrsHistory());
watchEffect(() => (activeQuery.value = MONITORING_PAGE_QUERIES[currentDefinition.value]));
</script>
<template>
  <FieldsValues
    :module="currentDefinition"
    :fields="SENSOR_VALUES"
    :data="[data?.modules[currentDefinition]?.sensorValues]"
  >
    <header class="col-span-full flex justify-between max-2xl:flex-col max-2xl:gap-6">
      <span class="text-3xl capitalize">{{ t("thrs.views.sensors.title") }}</span>
      <FieldsFilter />
    </header>

    <FieldsValuesEmpty />

    <template #field>
      <FieldHeader />
      <FieldCurrent :format="formatInt" />
    </template>
  </FieldsValues>

  <FieldsValues
    :module="currentDefinition"
    :fields="CONTROL_VALUES"
    :data="[data?.modules[currentDefinition]?.controlValues]"
  >
    <header
      class="col-span-full mt-10 flex justify-between max-2xl:flex-col max-2xl:gap-6 2xl:items-center"
    >
      <span class="text-3xl capitalize">{{ t("thrs.views.controls.title") }}</span>
      <FieldsFilter />
    </header>

    <FieldsValuesEmpty />

    <template #field>
      <FieldCurrent :format="formatInt" />
    </template>
  </FieldsValues>
</template>
