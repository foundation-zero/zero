<script setup lang="ts">
import { formatNumber } from "@/lib/utils";
import {
  extractField,
  parseSchema,
  parseSchemaNested,
  SchemaComponent,
  UndeterminedField,
  useThrsStore,
} from "@/stores/thrs";
import { JSONSchemaObject } from "@apidevtools/json-schema-ref-parser/dist/lib/types";
import { Button } from "@components/shadcn/button";
import { Label } from "@components/shadcn/label";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@components/shadcn/number-field";
import FieldEdit from "@modules/thrs/FieldEdit.vue";
import ValueTable from "@modules/thrs/ValueTable.vue";
import { computedAsync } from "@vueuse/core";
import { useObservable } from "@vueuse/rxjs";
import { computed, shallowRef, watch } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const thrs = useThrsStore();
await thrs.initialize();

const sensorValues = useObservable(thrs.sensorValues);
const controlValues = useObservable(thrs.controlValues);
const simulationStatus = useObservable(thrs.simulationStatus);
const modes = useObservable(thrs.allowedModes);
const schemas = useObservable(thrs.schemas);

const isSimulation = computed(() => simulationStatus);

const sendConnect = async () => {
  await thrs.sendMessage("thrs/simulation/connect", {});
};
const pickMode = async (mode: string) => {
  await thrs.sendMessage("thrs/simulation/mode", { mode });
};
const sendReset = async () => {
  await thrs.sendMessage("thrs/simulation/reset", {});
};
const sendValues = async () => {
  await thrs.sendMessage("thrs/simulation/set_values", {
    simulation_inputs: simulationInputsValue.value,
    control_params: controlParametersValue.value,
    control_mode: controlModeValue.value.control_mode,
  });
};
const sendStart = async () => {
  await thrs.sendMessage("thrs/simulation/start", {
    start_time: new Date().toISOString(),
    ticks: ticks.value,
  });
};
const sendRun = async () => {
  await thrs.sendMessage("thrs/simulation/run", {
    ticks: ticks.value,
  });
};

watch(schemas, (newSchemas) => {
  if (newSchemas) {
    simulationInputsValue.value = newSchemas.simulation_inputs_values;
  }
});

const simulationInputs = computedAsync<SchemaComponent[]>(async () => {
  if (!schemas.value) return [];

  return parseSchemaNested(schemas.value.simulation_inputs);
});

const controlParameters = computedAsync<UndeterminedField[]>(async () => {
  if (!schemas.value) return [];

  return parseSchema(schemas.value.control_params);
});

const controlModes = computedAsync<UndeterminedField | null>(async () => {
  if (!schemas.value) return null;

  return await extractField("control_mode", schemas.value.control_modes as JSONSchemaObject);
});

const controlModeValue = shallowRef<{ control_mode?: string }>({});

const controlParametersValue = shallowRef({});
const simulationInputsValue = shallowRef({});

const ticks = shallowRef(60);

const format = formatNumber(2);
</script>
<template>
  <div class="grid grid-cols-2 gap-4">
    <div>
      <h1 class="mb-4 text-2xl font-bold">{{ t("views.thrs.hmi.title") }}</h1>
      <template v-if="isSimulation">
        <h2 class="mb-2 text-xl font-semibold">{{ t("views.thrs.hmi.sensorValues") }}</h2>
        <Button @click="sendReset">{{ t("views.thrs.hmi.reset") }}</Button>
        <Button
          v-if="simulationStatus?.status === 'available'"
          @click="sendConnect"
          >{{ t("views.thrs.hmi.connect") }}</Button
        >
        <div v-if="simulationStatus?.status === 'mode_picking' && modes">
          <Button
            v-for="mode in modes.modes"
            :key="mode"
            @click="pickMode(mode)"
          >
            {{ mode }}
          </Button>
        </div>
        <div v-if="simulationStatus?.status === 'ready_to_start'">
          <Button @click="sendStart">{{ t("views.thrs.hmi.start") }}</Button>
        </div>
        <div v-if="simulationStatus?.status === 'ready_to_run'">
          <Button @click="sendRun">{{ t("views.thrs.hmi.run") }}</Button>
        </div>
        <div
          v-if="
            simulationStatus?.status && ['value_setting', 'ran'].includes(simulationStatus?.status)
          "
        >
          <Button @click="sendValues">{{ t("views.thrs.hmi.setValues") }}</Button>
        </div>
        <div
          v-if="
            simulationStatus?.status &&
            ['ready_to_start', 'ready_to_run', 'ran'].includes(simulationStatus?.status)
          "
        >
          <NumberField
            id="ticks"
            v-model="ticks"
            :min="1"
            :max="300"
          >
            <Label for="ticks">{{ t("views.thrs.hmi.seconds") }}</Label>
            <NumberFieldContent>
              <NumberFieldDecrement />
              <NumberFieldInput />
              <NumberFieldIncrement />
            </NumberFieldContent>
          </NumberField>
        </div>
      </template>
      <h2 class="mb-2 text-xl font-semibold">{{ t("views.thrs.hmi.sensorValues") }}</h2>
      <ValueTable
        v-if="sensorValues"
        :values="sensorValues"
        :format="format"
      />
      <h2 class="mb-2 text-xl font-semibold">{{ t("views.thrs.hmi.controlValues") }}</h2>
      <ValueTable
        v-if="controlValues"
        :values="controlValues"
        :format="format"
      />
    </div>
    <div>
      <template v-if="isSimulation && schemas">
        <div
          v-if="
            simulationStatus?.status &&
            ['value_setting', 'ran', 'ready_to_start', 'ready_to_run', 'running'].includes(
              simulationStatus?.status,
            )
          "
        >
          <h2 class="mb-2 text-xl font-semibold">{{ t("views.thrs.hmi.controlMode") }}</h2>
          <FieldEdit
            v-if="controlModes"
            v-model="controlModeValue"
            :field="controlModes"
          />
          <h2 class="mb-2 text-xl font-semibold">
            {{ t("views.thrs.hmi.controlParameters") }}
          </h2>
          <FieldEdit
            v-for="field in controlParameters"
            :key="field.name"
            v-model="controlParametersValue"
            :field="field"
          />
          <h2 class="mb-2 text-xl font-semibold">
            {{ t("views.thrs.hmi.simulationInputs") }}
          </h2>
          <div
            v-for="component in simulationInputs"
            :key="component.name"
          >
            <h3 class="text-lg font-semibold">{{ component.name }}</h3>
            <FieldEdit
              v-for="field in component.fields"
              :key="field.name"
              v-model="simulationInputsValue"
              :field="field"
            />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
