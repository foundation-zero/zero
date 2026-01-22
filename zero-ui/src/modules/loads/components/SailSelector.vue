<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import { Popover } from "@/components/ui/popover";
import PopoverContent from "@/components/ui/popover/PopoverContent.vue";
import PopoverTrigger from "@/components/ui/popover/PopoverTrigger.vue";
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { POSITION_GROUPS, SailId } from "../lib/consts.sails";
import { useVariablesStore } from "../stores/variables";
import { PositionId } from "../types";
import {
  SailSelector,
  SailSelectorGroup,
  SailSelectorGroupLabel,
  SailSelectorItem,
  SailSelectorPosition,
} from "./sail-selector";

const { t } = useI18n();

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const onSelect = (position: PositionId, sailId: SailId) => {
  if (selectedSails.value[position] === sailId) {
    selectedSails.value[position] = null;
  } else {
    selectedSails.value[position] = sailId;
  }
  setSelectedSails(selectedSails.value);
};

const { selectedSails } = toRefs(useVariablesStore());
const { setSelectedSails } = useVariablesStore();
</script>

<template>
  <Popover :class="cn(props.class)">
    <PopoverTrigger as-child>
      <Button variant="default">{{ t("views.loads.main.editSailset") }}</Button>
    </PopoverTrigger>
    <PopoverContent
      class="rounded-none border-none bg-transparent shadow-none ring-0 max-md:w-svw max-md:px-2"
    >
      <SailSelector>
        <SailSelectorGroup
          v-for="group in POSITION_GROUPS"
          :key="group.name"
          :group="group"
        >
          <SailSelectorGroupLabel>{{ group.name }}</SailSelectorGroupLabel>
          <SailSelectorPosition
            v-for="position in group.positions"
            :key="position.position"
          >
            <SailSelectorItem
              v-for="sail in position.sails"
              :key="sail.id"
              :model-value="selectedSails[position.position] === sail.id"
              @update:model-value="onSelect(position.position, sail.id)"
            >
              {{ sail.name }}
            </SailSelectorItem>
          </SailSelectorPosition>
        </SailSelectorGroup>
      </SailSelector>
    </PopoverContent>
  </Popover>
</template>
