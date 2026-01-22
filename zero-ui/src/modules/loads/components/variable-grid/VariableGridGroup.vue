<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes } from "vue";
import { getContext } from ".";
import { useVariablesStore } from "../../stores/variables";
import { Variable, VariableUnit } from "../../types";

const { getVariableById } = useVariablesStore();

const { type } = getContext();
const props = defineProps<{ items: string[]; class?: HTMLAttributes["class"] }>();
const variables = computed<Variable[]>(() =>
  props.items.map((id) => getVariableById(id).value).filter<Variable>((v): v is Variable => !!v),
);

const onOffs = computed(
  () => variables.value.filter(({ variable }) => variable.unit === VariableUnit.Bool).length,
);

const size = computed(() => {
  // Assumption: mast locks are never grouped with other variable types
  // Mast lock is 2/3 size of numerical card
  if (onOffs.value > 0) return Math.ceil((onOffs.value * 2) / 3);

  // In case of numerical view: each card has size 1
  if (type.value === "numerical") {
    return variables.value.length;
  }

  // In case of graphical view: variables with targets take double size
  return variables.value.reduce((size, variable) => {
    if (
      variable.reference?.target !== undefined &&
      variable.variable?.unit === VariableUnit.Ratio
    ) {
      return size + 2;
    }

    return size + 1;
  }, 0);
});
</script>

<template>
  <div
    v-if="size > 0"
    :class="
      cn(
        'grid gap-3 lg:gap-4',
        {
          'col-span-1': size === 1,
          [`col-span-2 sm:col-span-${Math.min(size, 3)} md:col-span-${Math.min(size, 4)} lg:col-span-${Math.min(size, 5)} xl:col-span-${Math.min(size, 6)}`]:
            size > 1,
          [`grid-cols-${onOffs}`]: onOffs > 1,
          [`grid-cols-2 sm:grid-cols-${Math.min(size, 3)} md:grid-cols-${Math.min(size, 4)} lg:grid-cols-${Math.min(size, 5)} xl:grid-cols-${Math.min(size, 6)}`]:
            size > 1 && onOffs === 0,
        },
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
