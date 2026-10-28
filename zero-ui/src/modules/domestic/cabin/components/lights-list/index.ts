import { DomesticLightingGroups } from "@/modules/domestic/gql/graphql";
import { Maybe } from "graphql/jsutils/Maybe";
import { inject, Ref } from "vue";

export { default as LightGroup } from "./LightGroup.vue";

export type LightsContext = {
  commit: (group: DomesticLightingGroups, level: Ref<Maybe<number>>) => void;
};
export const getContext = (): LightsContext => {
  const commit = inject("commit") as (
    group: DomesticLightingGroups,
    level: Ref<Maybe<number>>,
  ) => void;

  if (!commit) {
    throw new Error("LightGroupItem components must be used within a LightsProvider");
  }

  return {
    commit,
  };
};
