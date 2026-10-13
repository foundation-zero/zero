<script setup lang="ts">
import { ExpansionTank } from "../../../components/expansion-tank";
import { ExpansionValve } from "../../../components/expansion-valve";
import { TagLabelInstance } from "../../../instances";
</script>

<template>
  <ExpansionTank
    x="1215"
    y="165"
  />
  <TagLabelInstance
    :target-x="1215"
    :target-width="36"
    y="220"
    tag-id="1040-01"
  />
  <ExpansionValve
    x="1145"
    y="145"
  />
  <TagLabelInstance
    x="1165"
    y="145"
    tag-id="1041-01"
  />
</template>
