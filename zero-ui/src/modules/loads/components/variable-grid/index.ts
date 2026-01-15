import { createContext } from "reka-ui";
import { Ref } from "vue";
import { CardType } from "../../types";

export { default as VariableGrid } from "./VariableGrid.vue";
export { default as VariableGridGroup } from "./VariableGridGroup.vue";
export { default as VariableGridHeader } from "./VariableGridHeader.vue";
export { default as VariableGridItem } from "./VariableGridItem.vue";

export type VariableGridContext = {
  type: Ref<CardType>;
};

export const [getContext, provideContext] =
  createContext<VariableGridContext>("loads.variable-grid");
