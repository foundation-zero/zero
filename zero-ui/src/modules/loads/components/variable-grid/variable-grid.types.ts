import { BreakpointsZero } from "@/modules/common/lib/consts";
import { Ref } from "vue";
import { VariableGroup } from "../../lib/consts.dashboards";
import { CardType, MaybeVariable, SailPositionGroup, Variable } from "../../types";

export type VariableGridContext = {
  groups: Ref<VariableGroup[]>;
  type: Ref<CardType>;
  dynamicDashboard: Ref<boolean>;
  variables: Ref<MaybeVariable[]>;
  positionGroups: Ref<SailPositionGroup[]>;
};

export type GridBreakpoints = keyof BreakpointsZero | "";

export interface GridGroup {
  size: number;
  group: VariableGroup<Variable>;
  variables: Variable[];
  hasBooleans: boolean;
}
