<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";

defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    :height="20"
    :width="44"
    class="whitespace-nowrap"
  >
    {{ tagId }}
  </Label>
</template>
