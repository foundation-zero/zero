import { ComputedRef, Ref } from "vue";
import { ReferenceThresholds, VariableState, VariableUnit } from "../../types";

export type PositionCardContext = {
  state: ComputedRef<VariableState>;
  value: Ref<number | undefined | null>;
  thresholds?: Ref<Partial<ReferenceThresholds> | undefined>;
  type: Ref<VariableUnit>;
};
