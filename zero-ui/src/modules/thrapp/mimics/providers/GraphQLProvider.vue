<script setup lang="ts" generic="K extends keyof THRS['modules']">
import { capitalizeFirst } from "@/modules/common/lib/utils";
import { QUERIES } from "@/modules/thrs/lib/consts";
import { THRS, ThrsDefinitions, ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import {
  ControlComponentType,
  ControlDefinitionMap,
  ControllerStateComponentType,
  ControllerStateDefinitionMap,
  ControlValues,
  ParameterDefinitionMap,
  ParametersType,
  SensorComponentType,
  SensorDefinitionMap,
} from "@/modules/thrs/types";
import { gql } from "@urql/vue";
import { computed, Ref, toRefs, unref } from "vue";
import { createMimicDataProvider, ModuleField } from ".";
import { useAutomaticMode } from "../../state";
import { MimicComponentState } from "../components";

const { data } = toRefs(useThrsHistory());
const { refresh, mutate } = useThrsHistory();

const getSensorValue = <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<SensorDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.sensorValues?.[
        field as keyof ThrsModules[Module]["sensorValues"]
      ],
  );

const getControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ControlDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.controlValues?.[
        field as keyof ThrsModules[Module]["controlValues"]
      ],
  );

const getParameterValue = <Type extends ParametersType, Module extends keyof ThrsDefinitions>([
  _type,
  module,
  field,
]: ModuleField<Type, Module>): Ref<ParameterDefinitionMap[Type] | undefined> =>
  computed(
    () =>
      data.value?.modules?.[module]?.parameters?.[field as keyof ThrsModules[Module]["parameters"]],
  );

const getControllerState = <
  Type extends ControllerStateComponentType,
  Module extends keyof ThrsDefinitions,
>([_type, module, field]: ModuleField<Type, Module>): Ref<
  ControllerStateDefinitionMap[Type] | undefined
> =>
  computed(
    () =>
      data.value?.modules?.[module]?.controllerState?.[
        field as keyof ThrsModules[Module]["controllerState"]
      ],
  );

const PARAMETER_INPUT_TYPES: Partial<Record<ParametersType, string>> = {
  [ParametersType.Disabled]: "Boolean!",
  [ParametersType.Enabled]: "Boolean!",
  [ParametersType.Flow]: "Float!",
  [ParametersType.FlowControl]: "Float!",
  [ParametersType.Level]: "Float!",
  [ParametersType.Ratio]: "Float!",
  [ParametersType.Temperature]: "Float!",
  [ParametersType.Tuning]: "[Float!]!",
  [ParametersType.Dutypoint]: "Float!",
  [ParametersType.dT]: "Float!",
};

const setParameter = async <Type extends ParametersType, Module extends keyof ThrsDefinitions>(
  source: ModuleField<Type, Module>,
  value: ParameterDefinitionMap[Type],
) => {
  const inputType = PARAMETER_INPUT_TYPES[source[0]];

  if (!inputType) {
    throw new Error(`No input type defined for parameter type ${source[0]}`);
  }

  const mutation = `${source[1]}ParameterSet${capitalizeFirst(source[2])}`;
  const query = gql`mutation ($input: ${inputType}) {
          ${mutation}(value: $input) {
            ${QUERIES[source[1]].parameters}
          }
      }`;

  const result = await mutate(query, {
    input: value,
  });

  await refresh();

  if (result.error) {
    throw result.error;
  }
};

const CONTROL_INPUT_TYPES: Partial<Record<ControlComponentType, string>> = {
  [ControlComponentType.Pump]: "PumpInputType!",
  [ControlComponentType.Valve]: "ValveInputType!",
  [ControlComponentType.Heatpump]: "HeatPumpInputType!",
};

const setControlValue = async <
  Type extends ControlComponentType,
  Module extends keyof ThrsDefinitions,
>(
  source: ModuleField<Type, Module>,
  value: ControlValues<Type>,
) => {
  const inputType = CONTROL_INPUT_TYPES[source[0]];

  if (!inputType) {
    throw new Error(`No input type defined for control type ${source[0]}`);
  }

  const mutation = `${source[1]}ControlSet${capitalizeFirst(source[2])}`;
  const query = gql`mutation ($input: ${inputType}) {
          ${mutation}(component: $input) {
            ${QUERIES[source[1]].controlValues}
          }
      }`;

  const result = await mutate(query, {
    input: { ...value, __typename: undefined },
  });

  await refresh();

  if (result.error) {
    throw result.error;
  }
};

const isAutomaticMode = useAutomaticMode();

createMimicDataProvider({
  getSensorValue,
  getControlValue,
  getParameter: getParameterValue,
  getControllerState,
  setParameter,
  setControlValue,
  getComponentState: (state) =>
    computed(() => {
      if (!isAutomaticMode.value) {
        return MimicComponentState.Manual;
      } else {
        return unref(state) ?? MimicComponentState.Normal;
      }
    }),
});
</script>

<template>
  <slot />
</template>
