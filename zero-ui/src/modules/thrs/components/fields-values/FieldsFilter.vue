<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { getContext } from ".";

const { series, selected } = getContext();
</script>

<template>
  <ToggleGroup
    v-model:model-value="selected"
    variant="outline"
    type="multiple"
    class="col-span-full"
  >
    <template
      v-for="[field, serie] in series"
      :key="field"
    >
      <ToggleGroupItem
        v-if="serie.length"
        :value="field"
        class="h-auto w-auto min-w-auto px-4 py-3 text-base capitalize"
        :aria-label="`Toggle ${field}`"
      >
        {{ field }}
        <Badge
          class="py-0"
          variant="secondary"
        >
          {{ serie.length }}
        </Badge>
      </ToggleGroupItem>
    </template>
  </ToggleGroup>
</template>
