<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import AlertBox from "../components/AlertBox.vue";
import FieldCurrent from "../components/fields-values/FieldCurrent.vue";
import FieldHeader from "../components/fields-values/FieldHeader.vue";
import FieldHistory from "../components/fields-values/FieldHistory.vue";
import FieldsFilter from "../components/fields-values/FieldsFilter.vue";
import FieldsValues from "../components/fields-values/FieldsValues.vue";
import FieldsValuesEmpty from "../components/fields-values/FieldsValuesEmpty.vue";
import SimulationControls from "../components/SimulationControls.vue";
import { SIMULATION, SIMULATION_FIELDS } from "../lib/consts";
import { useSimulationStore } from "../stores/simulation";

const { t } = useI18n();

const FIELDS = Array.from(new Set(Object.values(SIMULATION_FIELDS).flat()));
const { activeSimulationType } = toRefs(useSimulationStore());
</script>
<template>
  <template v-if="activeSimulationType">
    <FieldsValues
      module="simulation"
      :fields="FIELDS"
      :definitions="[
        SIMULATION.outputs[activeSimulationType!],
        SIMULATION.inputs[activeSimulationType!],
      ]"
    >
      <header class="col-span-full flex justify-between max-2xl:flex-col max-2xl:gap-6">
        <span class="text-3xl capitalize">{{ t("thrs.views.simulation.outputs") }}</span>
        <FieldsFilter />
      </header>

      <FieldsValuesEmpty />

      <template #field>
        <FieldHeader />
        <FieldCurrent :format="formatInt" />
        <FieldHistory />
      </template>
    </FieldsValues>

    <header class="mt-8 mb-4 text-3xl capitalize">
      {{ t("thrs.views.simulation.inputs") }}
    </header>

    <SimulationControls :type="activeSimulationType" />
  </template>

  <AlertBox v-else>
    {{ t("thrs.views.simulation.noActive") }}
  </AlertBox>
</template>
