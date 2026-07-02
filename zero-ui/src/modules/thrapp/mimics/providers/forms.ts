import { capitalizeFirst, toEntries, unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { QUERIES } from "@/modules/thrs/lib/consts";
import { ControlComponentType, ControlDefinitionMap } from "@/modules/thrs/types";
import { gql, useClientHandle } from "@urql/vue";
import { isEmpty } from "lodash";
import { computed, inject, provide, ref, Ref } from "vue";
import { getMimicDataProvider, ModuleField, provideFieldValue, provideFieldValueField } from ".";
import { useAutomaticMode } from "../../state";

export const enum MutationType {
  Control = "control",
  Parameter = "parameter",
}

const CONTROL_INPUT_TYPES: Partial<Record<ControlComponentType, string>> = {
  [ControlComponentType.Pump]: "PumpInputType!",
  [ControlComponentType.Valve]: "ValveInputType!",
  [ControlComponentType.Heatpump]: "HeatPumpInputType!",
};

export const INPUT_TYPES = {
  [MutationType.Control]: CONTROL_INPUT_TYPES,
};

export interface ControlValueFormContext<Control extends ControlComponentType> {
  isDirty: Ref<boolean>;
  error: Ref<string | undefined>;
  isPending: Ref<boolean>;
  editable: Ref<boolean>;
  data: Ref<ControlDefinitionMap[Control] | undefined>;
  submit(): void;
  undo(): void;
  update<
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>,
  >(
    field: Key,
    value: Value,
  ): void;
  getValue<
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>,
  >(
    field?: Key,
  ): Ref<Value | undefined>;
}

export const createFormContext = <Control extends ControlComponentType>(
  source: ModuleField<Control>,
): ControlValueFormContext<Control> => {
  const { getControlValue } = getMimicDataProvider();

  const control = getControlValue(source);

  const automaticMode = useAutomaticMode();
  const dirtyValues = ref<Partial<Record<string, unknown>>>({});
  const currentValues = computed(() =>
    Object.fromEntries(toEntries(control.value!, (_, value) => unstamp(value))),
  );
  const isDirty = computed(() => !isEmpty(dirtyValues.value));
  const error = ref<string>();
  const isPending = ref(false);
  const editable = computed(() => control.value != undefined);

  const inputType = INPUT_TYPES[MutationType.Control][source[0]];
  const mutation = `${source[1]}${capitalizeFirst(MutationType.Control)}Set${capitalizeFirst(source[2])}`;
  const query = gql`mutation ($input: ${inputType!}) {
        ${mutation}(component: $input) {
          ${QUERIES[source[1]].controlValues}
        }
    }`;

  const { client } = useClientHandle();

  async function submit() {
    if (!editable.value || !control.value || automaticMode.value || isPending.value) return;

    error.value = undefined;
    isPending.value = true;

    const result = await client.mutation(query, {
      input: { ...currentValues.value, ...dirtyValues.value, __typename: undefined },
    });

    isPending.value = false;
    error.value = result.error?.message;

    undo();
  }

  function undo() {
    dirtyValues.value = {};
  }

  function update<
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>,
  >(field: Key, value: Value) {
    dirtyValues.value[field as string] = value;
  }

  function getValue<
    Key extends keyof ControlDefinitionMap[Control],
    Value extends Unstamp<ControlDefinitionMap[Control][Key]>,
  >(field?: Key) {
    return computed(() => {
      if (!field) {
        return undefined;
      } else {
        return <Value | undefined>(
          (dirtyValues.value[field as string] ?? unstamp(control.value?.[field]))
        );
      }
    });
  }

  return {
    isDirty,
    error,
    isPending,
    data: control,
    editable,
    submit,
    undo,
    update,
    getValue,
  };
};

export const injectControlValueForm = <Control extends ControlComponentType>() =>
  inject<ControlValueFormContext<Control>>("ControlValueForm");

export const provideControlValueForm = <Control extends ControlComponentType>(
  value: ControlValueFormContext<Control>,
) => provide("ControlValueForm", value);

export const provideControlValue = <
  Control extends ControlComponentType,
  Key extends keyof ControlDefinitionMap[Control],
>(
  source: ModuleField<Control>,
  field?: Key,
) => {
  const value = getControlValue(source, field);
  provideFieldValueField(field as string | undefined);
  provideFieldValue(value);
  return value;
};

const getControlValue = <
  Control extends ControlComponentType,
  Key extends keyof ControlDefinitionMap[Control],
  Value extends Unstamp<ControlDefinitionMap[Control][Key]>,
>(
  source: ModuleField<Control>,
  field?: Key,
): Ref<Value | undefined> => {
  const form = injectControlValueForm<Control>();
  const automaticMode = useAutomaticMode();

  if (!form || automaticMode.value) {
    const { getControlValue } = getMimicDataProvider();
    const control = getControlValue(source);
    return computed(() =>
      !field ? undefined : (unstamp(control.value?.[field]) as Value | undefined),
    );
  } else {
    const value = form.getValue<Key, Value>(field);

    return computed({
      get() {
        return value.value;
      },
      set(value: Value) {
        if (field) {
          form.update(field, value);
        }
      },
    });
  }
};
