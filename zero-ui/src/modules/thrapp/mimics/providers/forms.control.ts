import { toEntries, unstamp } from "@/modules/common/lib/utils";
import { Unstamp } from "@/modules/common/types";
import { ControlComponentType, ControlDefinitionMap, ControlValues } from "@/modules/thrsim/types";
import { isEmpty } from "lodash";
import { computed, ref, Ref } from "vue";
import {
  DEFAULT_CONTROL_FIELD_VALUE_FIELD,
  getMimicDataProvider,
  ModuleField,
  provideFieldValue,
  provideFieldValueField,
} from ".";
import { useAutomaticMode } from "../../state";
import { injectValueForm, provideValueForm, ValueFormContext } from "./forms";

export interface ControlValueFormContext<
  Control extends ControlComponentType,
> extends ValueFormContext {
  data: Ref<ControlDefinitionMap[Control] | undefined>;
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
  const { getControlValue, setControlValue } = getMimicDataProvider();

  const control = getControlValue(source);

  const automaticMode = useAutomaticMode();
  const dirtyValues = ref({} as Partial<ControlValues<Control>>);
  const currentValues = computed(
    () =>
      Object.fromEntries(
        toEntries(control.value!, (_, value) => unstamp(value)),
      ) as ControlValues<Control>,
  );
  const isDirty = computed(() => !isEmpty(dirtyValues.value));
  const error = ref<string>();
  const isPending = ref(false);
  const isEditable = computed(() => control.value != undefined && !automaticMode.value);

  async function submit() {
    if (!isEditable.value || !control.value || automaticMode.value || isPending.value) return;

    error.value = undefined;
    isPending.value = true;

    try {
      await setControlValue(source, {
        ...currentValues.value,
        ...dirtyValues.value,
      });
    } catch (err) {
      error.value = (err as Error).message;
    } finally {
      isPending.value = false;
      undo();
    }
  }

  function undo() {
    dirtyValues.value = {};
  }

  function update<
    Key extends keyof ControlValues<Control>,
    Value extends ControlValues<Control>[Key],
  >(field: Key, value: Value) {
    dirtyValues.value[field] = value;
  }

  function getValue<
    Key extends keyof ControlValues<Control>,
    Value extends ControlValues<Control>[Key],
  >(field?: Key) {
    return computed(() => {
      if (!field) {
        return undefined;
      } else {
        return <Value | undefined>(dirtyValues.value[field] ?? unstamp(control.value?.[field]));
      }
    });
  }

  return {
    isDirty,
    error,
    isPending,
    data: control,
    isEditable,
    submit,
    undo,
    update,
    getValue,
  };
};

export const provideControlValueForm = <Control extends ControlComponentType>(
  value: ControlValueFormContext<Control>,
) => {
  provideValueForm(value);
};

export const provideControlValue = <Control extends ControlComponentType>(
  source: ModuleField<Control>,
  field: keyof ControlDefinitionMap[Control] = DEFAULT_CONTROL_FIELD_VALUE_FIELD[source[0]],
  form: ControlValueFormContext<Control> | undefined = injectValueForm<
    ControlValueFormContext<Control>
  >(),
) => {
  const value = getControlValue(source, field, form);
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
  form?: ControlValueFormContext<Control>,
): Ref<Value | undefined> => {
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
