<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { AirTrapVesselInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const airTrapVessels = getTooltipContexts(MimicComponentType.AirTrapVessel, ["1084"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <AirTrapVesselInstance
      x="200"
      y="-30"
      :orientation="ComponentOrientation.Up"
      v-bind="airTrapVessels['1084']"
    />
    <TagLabelInstance
      x="230"
      y="-30"
      tag-id="1084"
    />
    <TagLabelInstance
      x="160"
      y="5"
      tag-id="1086"
    />
  </LayerFilter>
</template>
