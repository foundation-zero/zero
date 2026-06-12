<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { Label } from "../components/label";

defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <Label
    :x="x"
    :y="y"
    :width="30"
    :height="20"
  >
    {{ tagId }}
  </Label>
</template>
