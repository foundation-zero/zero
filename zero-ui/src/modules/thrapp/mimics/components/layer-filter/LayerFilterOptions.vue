<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { cn, tScoped } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";
import { LayerFilterOption, useLayerFilterContext } from "./layer-filter.provider";

const props = defineProps<{ options: LayerFilterOption[]; class?: HTMLAttributes["class"] }>();

const t = tScoped("thrapp.labels.layerFilters");
const { isFilterActive, setFilter } = useLayerFilterContext();
</script>

<template>
  <ul :class="cn('flex flex-col gap-2', props.class)">
    <li
      v-for="option in options"
      :key="option"
    >
      <label
        class="flex cursor-pointer items-center gap-4 text-sm leading-none font-medium whitespace-nowrap"
      >
        <Switch
          class="h-6 w-12"
          thumb-class="size-4 data-[state=checked]:translate-x-6.75 data-[state=unchecked]:translate-x-0.75 data-[state=unchecked]:bg-border"
          :model-value="isFilterActive(option)"
          @update:model-value="setFilter(option, $event)"
        />
        {{ t(option) }}
      </label>
    </li>
  </ul>
</template>
