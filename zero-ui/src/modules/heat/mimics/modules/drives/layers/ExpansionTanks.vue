<script setup lang="ts">
import { ExpansionTank } from "../../../components/expansion-tank";
import { ExpansionValve } from "../../../components/expansion-valve";
import { TagLabelInstance } from "../../../instances";
</script>

<template>
  <g>
    <ExpansionTank
      x="1612"
      y="102"
    />
    <TagLabelInstance
      x="1568"
      y="118"
      tag-id="1040-04"
    />
    <g transform="matrix(0 1 1 0 1657 71)">
      <ExpansionValve />
    </g>
    <TagLabelInstance
      x="1607"
      y="69"
      tag-id="1041-05"
    />
  </g>
</template>
