<script setup lang="ts">
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
</script>

<template>
  <g>
    <!-- Supply and return headers -->
    <TagLabelInstance
      :target-x="83.03"
      :target-width="502.94"
      y="30.6"
      tag-id="9001-02"
    />
    <TagLabelInstance
      :target-x="83.03"
      :target-width="502.94"
      y="592.3"
      tag-id="9001-02"
    />
    <TagLabelInstance
      :target-x="712.58"
      :target-width="524"
      y="30.6"
      tag-id="9002-01"
    />
    <TagLabelInstance
      :target-x="712.58"
      :target-width="524"
      y="592.3"
      tag-id="9002-01"
    />

    <!-- Pyranometers -->
    <TagLabelInstance
      x="1"
      y="242.5"
      tag-id="9045-1"
    />
    <TagLabelInstance
      x="18"
      y="446"
      tag-id="9045-1"
    />
  </g>
</template>
