<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends ControlDefinitions,
    Values extends ExtractAllValues<Definitions>
  "
>
import { ControlComponentType, ControlDefinitions, ExtractAllValues } from "@/modules/thrs/types";

import { QUERIES, THRSModules } from "@/modules/thrs/lib/consts";
import { type Component, computed, toRefs } from "vue";
import ModuleControls from "../components/controls/ModuleControls.vue";
import PumpControl from "../components/controls/PumpControl.vue";
import ValveControl from "../components/controls/ValveControl.vue";
import { useThrsHistory } from "../stores/history";

const props = defineProps<{
  module: K;
  definition: Definitions;
}>();

const { data } = toRefs(useThrsHistory());

const controlsData = computed(
  () => data.value?.modules[props.module]?.controlValues as Values | undefined,
);

const COMPONENTS: Record<ControlComponentType, Component> = {
  [ControlComponentType.Pump]: PumpControl,
  [ControlComponentType.Valve]: ValveControl,
  [ControlComponentType.Pcm]: ValveControl,
};
</script>
<template>
  <ModuleControls
    :controls="definition"
    :data="controlsData"
    :disabled="false"
  >
    <template #default="{ componentName, componentDefinition, setControlValues, values }">
      <component
        :is="COMPONENTS[componentDefinition.componentType]"
        :definition="componentDefinition"
        :module="module"
        :values="values"
        :query="QUERIES[module].controlValues"
        :component-name="componentName"
        :component-type="componentDefinition.componentType"
        :yard-tag="componentDefinition.yardTag"
        :valve-type="
          componentDefinition.componentType === ControlComponentType.Valve
            ? componentDefinition.valveType
            : undefined
        "
        @update:control-values="setControlValues"
      />
    </template>
  </ModuleControls>
</template>
