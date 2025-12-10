import { createContext } from "reka-ui";
import { Ref } from "vue";
import { ReferenceThresholds, VariableState } from "../../types";

export { default as PositionCard } from "./PositionCard.vue";

export type PositionCardContext = {
  state: Ref<VariableState>;
  value: Ref<number | undefined>;
  thresholds?: Ref<ReferenceThresholds | undefined>;
};

export const [getContext, provideContext] =
  createContext<PositionCardContext>("loads.position-card");
