import { ThrsModules, ThrsSimulationType } from "@/modules/thrs/lib/consts";
import { PID } from "@/modules/thrs/types";
import { unstamp } from "@common/lib/utils";
import { Stamped } from "@common/types";
import { useClientHandle } from "@urql/vue";
import { defineStore } from "pinia";
import { computed, ref, Ref, WritableComputedRef } from "vue";

type FormValue<T> = {
  value: WritableComputedRef<T>;
  isDirty: Ref<boolean>;
};
type Unstamp<T> = T extends Stamped<infer U> ? U : T;

const capitalizeFirst = (a: string) => {
  const f = a.substring(0, 1).toUpperCase();
  return `${f}${a.substring(1)}`;
};

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

export const enum MutationType {
  Control = "control",
  Parameter = "parameter",
  Simulation = "simulation",
}

export type InputType = {
  [MutationType.Control]: ["PumpInputType!", "ValveInputType!"];
  [MutationType.Parameter]: ["Float!", "[Float!]!"];
  [MutationType.Simulation]: [
    "ThrusterInputType!",
    "BoundaryInputType!",
    "PcsInputType!",
    "TemperatureBoundaryInputType!",
  ];
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

export const controlValuesForm = <
  Module extends keyof ThrsModules | ThrsSimulationType,
  Mutation extends MutationType,
  Input extends InputType[Mutation],
  A extends Ref<FieldObject | FieldType>,
  K extends ExtractRefKeys<A>,
  Form extends FormValues<A>,
>(
  module: Module,
  mutationType: Mutation,
  inputType: Input[number],
  componentName: string,
  values: A,
  fields: K[],
  returnValuesQuery: string,
  emit: (event: "update:controlValues", value: A["value"]) => void,
): {
  submit: () => Promise<void>;
  isSubmitting: Ref<boolean>;
  error: Ref<null | string>;
} & Form => {
  const refs = Object.fromEntries(
    fields.map((field: K) => [
      field,
      valueWithDirty(
        computed(() =>
          typeof values.value === "object" && !Array.isArray(values.value)
            ? values.value[field]
            : values.value,
        ),
      ),
    ]),
  );
  const isSubmitting = ref(false);
  const error = ref<null | string>(null);
  const { client } = useClientHandle();

  const submit = async () => {
    const input =
      typeof values.value === "object" && !Array.isArray(values.value)
        ? Object.fromEntries(Object.entries(refs).map(([key, { value }]) => [key, value.value]))
        : refs["value"].value.value;

    const mutation = `${module}${capitalizeFirst(mutationType)}Set${capitalizeFirst(componentName)}`;
    const query = `mutation ($input: ${inputType}) {
      ${mutation}(${mutationType == MutationType.Parameter ? "value" : "component"}: $input) {
        ${returnValuesQuery}
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
  } & Form;
};

defineStore("thrs", () => {});
