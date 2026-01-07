import { defineStore } from "pinia";
import { computed, Ref, ref } from "vue";
import { VARIABLES } from "../lib/consts.variables";
import { Variable } from "../types";

export const useVariablesStore = defineStore("loads-variables", () => {
  const variables: Ref<Variable<number | boolean>[]> = ref(VARIABLES);

  const getVariableById = <T extends number | boolean>(id: string) =>
    computed(() => variables.value.find((variable) => variable.id === id) as Variable<T>);

  return {
    variables,
    getVariableById,
  };
});
