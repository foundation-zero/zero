export { default as VariableCard } from "./VariableCard.vue";
export { default as VariableCardReferenceTarget } from "./VariableCardReferenceTarget.vue";
export { default as VariableCardReferenceThresholds } from "./VariableCardReferenceThresholds.vue";
export { default as VariableCardTitle } from "./VariableCardTitle.vue";
export { default as VariableCardValue } from "./VariableCardValue.vue";

import { createContext } from "reka-ui";
import { ComputedRef, Ref } from "vue";
import { ReferenceThresholds, VariableState, VariableUnit } from "../../types";

export type PositionCardContext = {
  state: ComputedRef<VariableState>;
  value: Ref<number | undefined | null>;
  thresholds?: Ref<Partial<ReferenceThresholds> | undefined>;
  type: Ref<VariableUnit>;
};

export const [getContext, provideContext] =
  createContext<PositionCardContext>("loads.variable-card");
