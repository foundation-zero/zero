<script setup lang="ts">
import { ModuleDefinition } from "@/modules/thrsim/types";

import { formatInt } from "@/modules/common/lib/utils";
import { CONTROL_FIELDS, DEFINITIONS, SENSOR_FIELDS } from "@/modules/thrsim/lib/consts";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  FieldCurrent,
  FieldHeader,
  FieldHistory,
  FieldsFilter,
  FieldsValues,
  FieldsValuesEmpty,
} from "../components/fields-values";

const { t } = useI18n();

const SENSOR_VALUES = Array.from(new Set(Object.values(SENSOR_FIELDS).flat()));
const CONTROL_VALUES = Array.from(new Set(Object.values(CONTROL_FIELDS).flat()));
const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);
</script>
<template>
  <FieldsValues
    :module="currentDefinition"
    :fields="SENSOR_VALUES"
    :definitions="[definition.sensorValues]"
  >
    <header class="col-span-full flex justify-between max-2xl:flex-col max-2xl:gap-6">
      <span class="text-3xl capitalize">{{ t("thrs.views.sensors.title") }}</span>
      <FieldsFilter />
    </header>

    <FieldsValuesEmpty />

    <template #field>
      <FieldHeader />
      <FieldCurrent :format="formatInt" />
      <FieldHistory />
    </template>
  </FieldsValues>

  <FieldsValues
    :module="currentDefinition"
    :fields="CONTROL_VALUES"
    :definitions="[definition.controlValues]"
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
      <FieldHistory />
    </template>
  </FieldsValues>
</template>
