import { LightingGroup } from "@/modules/domestic/types";
import { inject, Ref } from "vue";

export { default as LightGroup } from "./LightGroup.vue";

export type LightsContext = {
  commit: (group: LightingGroup, level: Ref<number>) => void;
};
export const getContext = (): LightsContext => {
  const commit = inject("commit") as (group: LightingGroup, level: Ref<number>) => void;

  if (!commit) {
    throw new Error("LightGroupItem components must be used within a LightsProvider");
  }

  return {
    commit,
  };
};
