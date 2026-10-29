import { Ref } from "vue";
import { SailId } from "../../lib/consts.sails";
import { PositionId, SailPositionGroup } from "../../types";

export type SailSelectorContext = {
  modelValue: Ref<SailId[]>;
  groups: SailPositionGroup[];
};

export type SailSelection = Record<PositionId, SailId | null>;
