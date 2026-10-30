import { capitalizeFirst } from "@/modules/common/lib/utils";
import { QUERIES } from "@/modules/thrapp/lib/consts";
import { ThrsDefinitions, ThrsModules } from "@/modules/thrapp/lib/consts.types";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
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
} from "@/modules/thrapp/types/thrs";
import { gql } from "@urql/vue";
import { computed, Ref, toRefs, unref } from "vue";
import { MimicDataProvider, ModuleField } from ".";
import { useAdvisoryEnabled, useAutomaticMode } from "../../state";
import { MimicComponentState } from "../components";

const PARAMETER_INPUT_TYPES: Partial<Record<ParametersType, string>> = {
  [ParametersType.Enabled]: "Boolean!",
  [ParametersType.Flow]: "Float!",
  [ParametersType.FlowControl]: "Float!",
  [ParametersType.Level]: "Float!",
  [ParametersType.Ratio]: "Float!",
  [ParametersType.Temperature]: "Float!",
  [ParametersType.Tuning]: "[Float!]!",
  [ParametersType.Dutypoint]: "Float!",
  [ParametersType.dT]: "Float!",
  [ParametersType.Duration]: "Float!",
  [ParametersType.Power]: "Float!",
};

const CONTROL_INPUT_TYPES: Partial<Record<ControlComponentType, string>> = {
  [ControlComponentType.Pump]: "PumpInputType!",
  [ControlComponentType.Valve]: "ValveInputType!",
  [ControlComponentType.Heatpump]: "HeatPumpInputType!",
};

export const useGraphQLDataProvider = (): MimicDataProvider => {
  const { data } = toRefs(useThrsHistory());
  const { refresh, mutate } = useThrsHistory();
  // Each view queries only the module parts it shows (see `queries.consts.ts`); flag missing parts.
  const missingWarnings = new Set<string>();
  const modulePart = <Module extends keyof ThrsDefinitions, Part extends keyof ThrsModules[Module]>(
    module: Module,
    part: Part,
  ): ThrsModules[Module][Part] | undefined => {
    const value = data.value?.modules?.[module]?.[part];
    const key = `${module}.${String(part)}`;

    if (import.meta.env.DEV && data.value && value === undefined && !missingWarnings.has(key)) {
      missingWarnings.add(key);
      console.warn(`"${key}" is shown, but the query of the view does not include it.`);
    }
    return value;
  };
  const isAutomaticMode = useAutomaticMode();
  const isAdvisoryEnabled = useAdvisoryEnabled();

  const getSensorValue = <Type extends SensorComponentType, Module extends keyof ThrsDefinitions>([
    _type,
    module,
    field,
  ]: ModuleField<Type, Module>): Ref<SensorDefinitionMap[Type] | undefined> =>
    computed(
      () =>
        modulePart(module, "sensorValues")?.[field as keyof ThrsModules[Module]["sensorValues"]],
    );

  const getControlValue = <
    Type extends ControlComponentType,
    Module extends keyof ThrsDefinitions,
  >([_type, module, field]: ModuleField<Type, Module>): Ref<
    ControlDefinitionMap[Type] | undefined
  > =>
    computed(
      () =>
        modulePart(module, "controlValues")?.[field as keyof ThrsModules[Module]["controlValues"]],
    );

  const getParameterValue = <Type extends ParametersType, Module extends keyof ThrsDefinitions>([
    _type,
    module,
    field,
  ]: ModuleField<Type, Module>): Ref<ParameterDefinitionMap[Type] | undefined> =>
    computed(
      () => modulePart(module, "parameters")?.[field as keyof ThrsModules[Module]["parameters"]],
    );

  const getControllerState = <
    Type extends ControllerStateComponentType,
    Module extends keyof ThrsDefinitions,
  >([_type, module, field]: ModuleField<Type, Module>): Ref<
    ControllerStateDefinitionMap[Type] | undefined
  > =>
    computed(
      () =>
        modulePart(module, "controllerState")?.[
          field as keyof ThrsModules[Module]["controllerState"]
        ],
    );

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
          ${mutation}(value: $input) {
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

  return {
    getSensorValue,
    getControlValue,
    getParameter: getParameterValue,
    getControllerState,
    setParameter,
    setControlValue,
    getComponentState: (state) =>
      computed(() => {
        if (!isAdvisoryEnabled.value) {
          return MimicComponentState.Normal;
        } else if (!isAutomaticMode.value) {
          return MimicComponentState.Manual;
        } else {
          return unref(state) ?? MimicComponentState.Normal;
        }
      }),
  };
};
