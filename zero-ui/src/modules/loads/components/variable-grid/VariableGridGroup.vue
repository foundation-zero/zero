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
  props.items
    .map((id) => getVariableById(id).value)
    .filter<Variable>((v): v is Variable => !!v && !!v.variable),
);

const onOffs = computed(
  () => variables.value.filter(({ variable }) => variable?.unit === VariableUnit.Bool).length,
);

const outerSize = computed(() => {
  // Assumption: mast locks are never grouped with other variable types
  // Mast lock is 2/3 size of numerical card
  if (onOffs.value > 0) return Math.ceil((onOffs.value / 3) * 2);

  // In case of numerical view: each card has size 1
  if (type.value === "numerical") {
    return variables.value.length;
  }

  // In case of graphical view: variables with targets take double size
  return variables.value.reduce((size, variable) => {
    if (
      variable.variable?.scaleMin !== undefined &&
      variable.variable?.scaleMax !== undefined &&
      (variable.variable?.unit === VariableUnit.Ratio ||
        variable.variable?.unit === VariableUnit.Tonne)
    ) {
      return size + 2;
    }

    return size + 1;
  }, 0);
});

const innerSize = computed(() => {
  if (onOffs.value > 0) {
    return outerSize.value * 3;
  }

  return outerSize.value;
});
</script>

<template>
  <div
    v-if="outerSize > 0"
    :class="
      cn(
        'grid gap-3 lg:gap-4',
        {
          'col-span-1': outerSize === 1,
          [`col-span-2 sm:col-span-${Math.min(outerSize, 3)} md:col-span-${Math.min(outerSize, 4)} lg:col-span-${Math.min(outerSize, 5)} xl:col-span-${Math.min(outerSize, 6)} 2xl:col-span-${Math.min(outerSize, 8)} 3xl:col-span-${Math.min(outerSize, 10)} 4xl:col-span-${Math.min(outerSize, 12)}`]:
            outerSize > 1,
          [`grid-cols-${Math.min(6, innerSize)} sm:grid-cols-${Math.min(9, innerSize)} md:grid-cols-${Math.min(12, innerSize)} lg:grid-cols-${Math.min(15, innerSize)} xl:grid-cols-${Math.min(18, innerSize)} 2xl:grid-cols-${Math.min(24, innerSize)}`]:
            onOffs > 1,
          [`grid-cols-2 sm:grid-cols-${Math.min(innerSize, 3)} md:grid-cols-${Math.min(innerSize, 4)} lg:grid-cols-${Math.min(innerSize, 5)} xl:grid-cols-${Math.min(innerSize, 6)} 2xl:grid-cols-${Math.min(innerSize, 8)} 3xl:grid-cols-${Math.min(innerSize, 10)} 4xl:grid-cols-${Math.min(innerSize, 12)}`]:
            outerSize > 1 && onOffs === 0,
        },
        props.class,
      )
    "
  >
    <slot />
    <slot
      v-for="variable in variables"
      :key="variable.variable?.id"
      name="item"
      :variable="variable"
    />
  </div>
</template>
