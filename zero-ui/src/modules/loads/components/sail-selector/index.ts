import { createContext } from "reka-ui";
import { Ref } from "vue";
import { SailId } from "../../lib/consts.sails";
import { PositionId, SailPositionGroup } from "../../types";

export { default as SailSelector } from "./SailSelector.vue";
export { default as SailSelectorGroup } from "./SailSelectorGroup.vue";
export { default as SailSelectorGroupLabel } from "./SailSelectorGroupLabel.vue";
export { default as SailSelectorItem } from "./SailSelectorItem.vue";
export { default as SailSelectorPosition } from "./SailSelectorPosition.vue";
export { default as SailSelectorTrigger } from "./SailSelectorTrigger.vue";

export type SailSelectorContext = {
  modelValue: Ref<SailId[]>;
  groups: SailPositionGroup[];
};

export const [injectRootContext, provideRootContext] =
  createContext<SailSelectorContext>("sail-selector");

export type SailSelection = Record<PositionId, SailId | null>;
