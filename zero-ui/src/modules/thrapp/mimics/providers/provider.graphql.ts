import { capitalizeFirst } from "@/modules/common/lib/utils";
import { isThrsApiModule } from "@/modules/thrapp/lib/consts";
import {
  MqttGraphqlModules,
  ThrsDefinitions,
  ThrsModules,
} from "@/modules/thrapp/lib/consts.types";
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

type ControllerInput = "parameters" | "controlValues";

const INPUT_TYPES: Record<ControllerInput, string> = {
  parameters: "Parameters",
  controlValues: "ControlValues",
};

// A module's controller takes its parameters and control values on the MQTT GraphQL API, each
// as one input object; the API returns once the parameters are stored and once the AMCS has
// actuated the control values. Only modules with a controller have them; the API names their
// input types after the module. The response is not used: the view's query is refreshed instead.
const controllerMutation = (module: keyof ThrsDefinitions, part: ControllerInput) => {
  if (!isThrsApiModule(module)) {
    throw new Error(`${module} has no controller`);
  }
  const inputType = `ThrsControl${capitalizeFirst(module)}${INPUT_TYPES[part]}Input`;
  return gql`
    mutation ($input: ${inputType}!) {
      thrs { controller { ${module} { ${part}(input: $input) { __typename } } } }
    }
  `;
};

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

  // Every value is stamped with now, so thrs-control takes it as the newest setpoint.
  const setControlValue = <Type extends ControlComponentType, Module extends keyof ThrsDefinitions>(
    [_type, module, field]: ModuleField<Type, Module>,
    values: ControlValues<Type>,
  ) => {
    const timeStamp = new Date().toISOString();
    const stamped = Object.fromEntries(
      Object.entries(values)
        .filter(([name]) => name !== "__typename")
        .map(([name, value]) => [name, { value, timeStamp }]),
    );
    return send(module, "controlValues", { [field]: stamped });
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
