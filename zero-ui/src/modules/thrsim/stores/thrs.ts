import i18n from "@/i18n";
import { PID } from "@/modules/common/types";
import { ThrsApiModule } from "@/modules/thrapp/lib/consts";
import { controllerMutation, stampedValues } from "@/modules/thrapp/lib/mqtt-graphql.utils";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { ThrsSimulationType } from "@/modules/thrsim/lib/consts";
import { unstamp } from "@common/lib/utils";
import { Stamped } from "@common/types";
import { useClientHandle } from "@urql/vue";
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
  Simulation = "simulation",
}

export type InputType = {
  [MutationType.Simulation]: [
    "ThrusterInputType!",
    "BoundaryInputType!",
    "FlowBoundaryInputType!",
    "PcsInputType!",
    "TemperatureBoundaryInputType!",
    "OverpressureTemperatureBoundaryInputType!",
    "HeatSourceInputType!",
    "ActiveHeatSourceInputType!",
    "UgridInputType!",
    "PropulsionDriveInputType!",
    "HvacExchangerInputType!",
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

// A control's form on thrsim's Controls page: sends the edited fields as the component's control
// values to the MQTT GraphQL API, which returns once the AMCS has actuated them, then refreshes
// the page's data.
export const controlForm = <
  A extends Ref<FieldObject>,
  K extends ExtractRefKeys<A>,
  Form extends FormValues<A>,
>(
  module: ThrsApiModule,
  componentName: string,
  values: A,
  fields: K[],
): {
  submit: () => Promise<void>;
  isSubmitting: Ref<boolean>;
  error: Ref<null | string>;
} & Form => {
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
    const history = useThrsHistory();
    try {
      isSubmitting.value = true;
      error.value = null;

      const result = await history.mutate(controllerMutation(module, "controlValues"), {
        input: { [componentName]: stampedValues(edited) },
      });
      if (result.error) {
        error.value = result.error.message;
        return;
      }
      await history.refresh();
      // The mutation returns once the AMCS has actuated the values, and the fields stay editable
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

  return { submit, isSubmitting, error, ...refs } as {
    submit: () => Promise<void>;
    isSubmitting: Ref<boolean>;
    error: Ref<null | string>;
  } & Form;
};

export const controlValuesForm = <
  Module extends ThrsSimulationType,
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
      ${mutation}(value: $input) {
        ${returnValuesQuery}
      }
    }`;
    try {
      isSubmitting.value = true;
      error.value = null;

      const result = await client.mutation(query, { input });
      if (result.error) {
        error.value = result.error.message;
        return;
      }
      const newControlValues = result.data?.[mutation];
      if (newControlValues === undefined) {
        error.value = i18n.global.t("thrs.labels.failedToSubmit");
        return;
      }
      emit("update:controlValues", newControlValues);
      for (const ref in refs) {
        refs[ref].isDirty.value = false;
      }
    } catch (err) {
      error.value =
        err instanceof Error ? err.message : i18n.global.t("thrs.labels.failedToSubmit");
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
