<script setup lang="ts">
import { ExpansionTank } from "../../../components/expansion-tank";
import { ExpansionValve } from "../../../components/expansion-valve";
import { TagLabelInstance } from "../../../instances";
</script>

<template>
  <ExpansionTank
    x="1108"
    y="135"
  />

  <ExpansionValve
    x="1050"
    y="108"
  />
  <TagLabelInstance
    :target-x="1050"
    :target-width="36"
    y="92"
    tag-id="1041-04"
  />
  <TagLabelInstance
    x="114"
    y="152"
    tag-id="1092"
  />
</template>
