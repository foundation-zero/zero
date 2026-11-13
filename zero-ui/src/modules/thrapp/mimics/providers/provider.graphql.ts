import {
  MqttGraphqlModules,
  ThrsDefinitions,
  ThrsModules,
} from "@/modules/thrapp/lib/consts.types";
import {
  ControllerInput,
  controllerMutation,
  stampedValues,
} from "@/modules/thrapp/lib/mqtt-graphql.utils";
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
import { computed, Ref, toRefs, unref } from "vue";
import { MimicDataProvider, ModuleField } from ".";
import { useAdvisoryEnabled, useAutomaticMode } from "../../state";
import { MimicComponentState } from "../components";

export const useGraphQLDataProvider = (): MimicDataProvider => {
  const { data } = toRefs(useThrsHistory());
  const { refresh, mutate } = useThrsHistory();
  // Each view queries only the module parts it shows (see `queries.consts.ts`); flag missing parts.
  const missingWarnings = new Set<string>();
  const modulePart = <
    Module extends keyof ThrsDefinitions,
    Part extends keyof MqttGraphqlModules[Module],
  >(
    module: Module,
    part: Part,
  ): MqttGraphqlModules[Module][Part] | undefined => {
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

  const send = async (
    module: keyof ThrsDefinitions,
    part: ControllerInput,
    input: Record<string, unknown>,
  ) => {
    const result = await mutate(controllerMutation(module, part), { input });

    await refresh();

    if (result.error) {
      throw result.error;
    }
  };

  const setParameter = <Type extends ParametersType, Module extends keyof ThrsDefinitions>(
    [_type, module, field]: ModuleField<Type, Module>,
    value: ParameterDefinitionMap[Type],
  ) => send(module, "parameters", { [field]: value });

  const setControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    [_type, module, field]: ModuleField<Type, Module>,
    values: Partial<ControlValues<Type>>,
  ) => send(module, "controlValues", { [field]: stampedValues(values) });

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
