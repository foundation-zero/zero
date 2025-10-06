import { Stamped } from "@/@types/thrs";
import { useClientHandle } from "@urql/vue";
import { defineStore } from "pinia";
import { computed, ref, Ref, WritableComputedRef } from "vue";

type FormValue<T> = {
  value: WritableComputedRef<T>;
  isDirty: Ref<boolean>;
};
type Unstamp<T> = T extends Stamped<infer U> ? U : never;

const INPUT_TYPES = {
  pump: "PumpInputType!",
  valve: "ValveInputType!",
};

const capitalizeFirst = (a: string) => {
  const f = a.substring(0, 1).toUpperCase();
  return `${f}${a.substring(1)}`;
};

export const controlValuesForm = <
  A extends Record<string, Stamped<boolean | number>>,
  K extends keyof A,
>(
  componentName: string,
  type: "pump" | "valve",
  fields: K[],
  controlValuesQuery: string,
  props: { controlValues: A },
  emit: (event: "update:controlValues", value: A) => void,
): { submit: () => Promise<void>; isSubmitting: Ref<boolean>; error: Ref<null | string> } & {
  [key in K]: FormValue<Unstamp<A[key]>>;
} => {
  const refs = Object.fromEntries(
    fields.map((field: K) => {
      const dirtyValue = ref<A[K] | null>(null);
      return [
        field,
        {
          value: computed<A[K]>({
            get() {
              return dirtyValue.value !== null
                ? dirtyValue.value
                : props.controlValues[field].value;
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
        } as FormValue<A[K]>,
      ];
    }),
  );
  const isSubmitting = ref(false);
  const error = ref<null | string>(null);
  const { client } = useClientHandle();

  const submit = async () => {
    const input = Object.fromEntries(
      Object.entries(refs).map(([key, { value }]) => [key, value.value]),
    );
    const mutation = `setThrustersControl${capitalizeFirst(componentName)}`;
    const query = `mutation ($input: ${INPUT_TYPES[type]}) {
      ${mutation}(component: $input) {
        ${controlValuesQuery}
      }
    }`;
    try {
      isSubmitting.value = true;
      error.value = null;

      const result = await client.mutation(query, { input });
      const newControlValues = result.data[mutation];
      emit("update:controlValues", newControlValues);
      for (const ref in refs) {
        refs[ref].isDirty.value = false;
      }
    } catch (_err) {
      error.value = "Failed to submit";
    } finally {
      isSubmitting.value = false;
    }
  };

  return { submit, isSubmitting, error, ...refs } as {
    submit: () => Promise<void>;
    isSubmitting: Ref<boolean>;
    error: Ref<null | string>;
  } & {
    [key in K]: FormValue<Unstamp<A[key]>>;
  };
};

defineStore("thrs", () => {});
