import { DomesticLightingGroups } from "@/modules/domestic/gql/graphql";
import { Maybe } from "graphql/jsutils/Maybe";
import { Ref } from "vue";

export type LightsContext = {
  commit: (group: DomesticLightingGroups, level: Ref<Maybe<number>>) => void;
};
