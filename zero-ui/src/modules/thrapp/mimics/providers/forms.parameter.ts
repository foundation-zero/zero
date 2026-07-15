import { ParameterDefinitionMap, ParametersType } from "@/modules/thrs/types";
import { useDebounceFn } from "@vueuse/core";
import { computed, ref, Ref } from "vue";
import { useRoute } from "vue-router";
import { getMimicDataProvider, ModuleField, provideFieldValue } from ".";
import { useAutomaticMode } from "../../state";
import { provideValueForm, ValueFormContext } from "./forms";

export interface ParameterValueFormContext<
  Parameter extends ParametersType,
> extends ValueFormContext {
  source: ModuleField<Parameter>;
  value: Ref<ParameterDefinitionMap[Parameter] | undefined>;
  update(value: ParameterDefinitionMap[Parameter]): void;
}

export const createParameterFormContext = <Parameter extends ParametersType>(
  source: ModuleField<Parameter>,
): ParameterValueFormContext<Parameter> => {
  const { getParameter, setParameter } = getMimicDataProvider();
  const { query } = useRoute();
  const parameter = getParameter(source);
  const hasFocus = query.parameter === source[2];
  const automaticMode = useAutomaticMode();
  const dirtyValue = ref<ParameterDefinitionMap[Parameter] | undefined>();
  const isDirty = computed(() => dirtyValue.value !== undefined);
  const error = ref<string>();
  const isPending = ref(false);
  const isEditable = computed(() => parameter.value != undefined && !!automaticMode.value);

  const _submit = useDebounceFn(submit, 1000);

  const value = computed(() =>
    dirtyValue.value !== undefined ? dirtyValue.value : parameter.value,
  );

  async function submit() {
    if (
      !isEditable.value ||
      parameter.value == undefined ||
      isPending.value ||
      dirtyValue.value === undefined
    )
      return;

    error.value = undefined;
    isPending.value = true;

    try {
      await setParameter(source, dirtyValue.value!);
    } catch (err) {
      error.value = (err as Error).message;
    } finally {
      isPending.value = false;
    }

    undo();
  }

  function undo() {
    dirtyValue.value = undefined;
  }

  function update(value: ParameterDefinitionMap[Parameter]) {
    dirtyValue.value = value;
    _submit();
  }

  return {
    isDirty,
    error,
    source,
    isPending,
    value,
    isEditable,
    hasFocus,
    submit,
    undo,
    update,
  };
};

export const provideParameterValueForm = <Parameter extends ParametersType>(
  form: ParameterValueFormContext<Parameter>,
) => {
  provideValueForm(form);
  provideFieldValue(getParameterValue(form));
};

const getParameterValue = <Parameter extends ParametersType>({
  value,
  update,
}: ParameterValueFormContext<Parameter>): Ref<ParameterDefinitionMap[Parameter] | undefined> =>
  computed({
    get() {
      return value.value;
    },
    set(value: ParameterDefinitionMap[Parameter]) {
      update(value);
    },
  });
