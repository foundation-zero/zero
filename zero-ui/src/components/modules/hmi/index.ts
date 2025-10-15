import { THRS, THRSModules } from "@/lib/consts";
import { useQuery } from "@urql/vue";
import { computed, Ref } from "vue";

export type ComponentWithType<T extends string> = {
  componentType: T;
};

export const queryFor = <
  Module extends keyof THRSModules,
  Values extends keyof THRSModules[Module],
>(
  module: Module,
  fieldName: Values,
  componentsQuery: string,
) =>
  computed(() => {
    return `query ${module}Values {
    modules {
      ${module} {
        ${String(fieldName)} {
          ${componentsQuery}
        }
      }
    }
  }`;
  });

export const queryPacked = <
  Module extends keyof THRSModules,
  Values extends keyof THRSModules[Module],
>(
  module: Module,
  fieldName: Values,
  query: Ref<string>,
) => {
  const { data, ...rest } = useQuery<THRS>({ query });

  return computed(() => ({ data: data.value?.modules[module][fieldName], ...rest }));
};
