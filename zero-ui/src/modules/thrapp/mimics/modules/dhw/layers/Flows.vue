<script setup lang="ts">
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import FlowBoosting from "../flows/FlowBoosting.vue";
import FlowFilling from "../flows/FlowFilling.vue";
import FlowInUse from "../flows/FlowInUse.vue";
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.Flows">
    <FlowInUse />
    <FlowFilling />
    <FlowBoosting />
  </LayerFilter>
</template>
