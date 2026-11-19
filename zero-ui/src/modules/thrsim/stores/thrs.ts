import i18n from "@/i18n";
import { PID } from "@/modules/common/types";
import { ControlledModule } from "@/modules/thrapp/lib/consts";
import { controllerMutation, valueInputs } from "@/modules/thrapp/lib/mqtt-graphql.utils";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { unstamp } from "@common/lib/utils";
import { Stamped } from "@common/types";
import { computed, ref, Ref, WritableComputedRef } from "vue";
import { useSimulationStore } from "./simulation";

type FormValue<T> = {
  value: WritableComputedRef<T>;
  isDirty: Ref<boolean>;
};
type Unstamp<T> = T extends Stamped<infer U> ? U : T;

const valueWithDirty = <T>(value: Ref<T>): FormValue<Unstamp<T>> => {
  const dirtyValue = ref<Unstamp<T> | null>(null);
  return {
    value: computed<Unstamp<T>>({
      get() {
        return dirtyValue.value !== null ? dirtyValue.value : unstamp(value.value);
      },
      set(value) {
        dirtyValue.value = value;
      },
    }),
    isDirty: computed({
      get() {
        return dirtyValue.value !== null;
      },
      set(v: boolean) {
        if (!v) {
          dirtyValue.value = null;
        }
      },
    }),
  } as FormValue<Unstamp<T>>;
};

export type FieldObject = Record<string, unknown>;
export type FieldType = boolean | string | number | PID;

export type ExtractRefKeys<A extends Ref<FieldObject | FieldType>> =
  A extends Ref<FieldObject> ? keyof A["value"] : "value";

export type FormValues<
  A extends Ref<FieldObject | FieldType>,
  K extends ExtractRefKeys<A> = ExtractRefKeys<A>,
> = {
  [key in K]: FormValue<key extends keyof A["value"] ? Unstamp<A["value"][key]> : A["value"]>;
};

type ValuesForm<Form> = {
  submit: () => Promise<void>;
  isSubmitting: Ref<boolean>;
  error: Ref<null | string>;
} & Form;

// A form over some fields of a component's values. Submitting sends the edited fields and clears
// the edits once sent; the sender reloads what the page shows.
const editedValuesForm = <
  A extends Ref<FieldObject>,
  K extends ExtractRefKeys<A>,
  Form extends FormValues<A>,
>(
  values: A,
  fields: K[],
  send: (inputs: Record<string, unknown>) => Promise<{ error?: { message: string } }>,
): ValuesForm<Form> => {
  const refs = Object.fromEntries(
    fields.map((field: K) => [field, valueWithDirty(computed(() => values.value[field]))]),
  );
  const isSubmitting = ref(false);
  const error = ref<null | string>(null);

  const submit = async () => {
    const edited = Object.fromEntries(
      Object.entries(refs)
        .filter(([_, { isDirty }]) => isDirty.value)
        .map(([key, { value }]) => [key, value.value]),
    );
    try {
      isSubmitting.value = true;
      error.value = null;

      const result = await send(valueInputs(edited));
      if (result.error) {
        error.value = result.error.message;
        return;
      }
      // The mutation returns once the change is confirmed, and the fields stay editable
      // meanwhile: a field changed during the wait keeps its edit for the next submit.
      for (const [field, ref] of Object.entries(refs)) {
        if (field in edited && ref.value.value === edited[field]) {
          ref.isDirty.value = false;
        }
      }
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : i18n.global.t("thrs.labels.failedToSubmit");
    } finally {
      isSubmitting.value = false;
    }
  };

  return { submit, isSubmitting, error, ...refs } as ValuesForm<Form>;
};

// A control's form on thrsim's Controls page: the edits go to the module controller's control
// values on the MQTT GraphQL API, which returns once the AMCS has actuated them.
export const controlForm = <
  A extends Ref<FieldObject>,
  K extends ExtractRefKeys<A>,
  Form extends FormValues<A>,
>(
  module: ControlledModule,
  componentName: string,
  values: A,
  fields: K[],
): ValuesForm<Form> =>
  editedValuesForm<A, K, Form>(values, fields, async (stamped) => {
    const history = useThrsHistory();
    const result = await history.mutate(controllerMutation(module, "controlValues"), {
      input: { [componentName]: stamped },
    });
    if (!result.error) await history.refresh();
    return result;
  });

// A simulation input's form on thrsim's Simulation page: the edits go to the simulator's inputs
// on the MQTT GraphQL API.
export const simulationInputsForm = <
  A extends Ref<FieldObject>,
  K extends ExtractRefKeys<A>,
  Form extends FormValues<A>,
>(
  componentName: string,
  values: A,
  fields: K[],
): ValuesForm<Form> =>
  editedValuesForm<A, K, Form>(values, fields, (stamped) =>
    useSimulationStore().setInputs({ [componentName]: stamped }),
  );
