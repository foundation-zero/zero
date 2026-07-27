<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { CheckValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const checkValves = THRUSTERS_MIMIC_DATA[MimicComponentType.CheckValve];
</script>

<template>
  <g>
    <CheckValveInstance
      x="561"
      y="522"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1213-01']"
      ><TagLabelInstance
        x="561"
        y="517"
        :tag-id="checkValves['1213-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="561"
      y="613"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1213-02']"
      ><TagLabelInstance
        x="561"
        y="608"
        :tag-id="checkValves['1213-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="960"
      y="345"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1217-01']"
      ><TagLabelInstance
        x="960"
        y="340"
        :tag-id="checkValves['1217-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>

    <CheckValveInstance
      x="960"
      y="453"
      :orientation="ComponentOrientation.Right"
      v-bind="checkValves['1217-02']"
      ><TagLabelInstance
        x="960"
        y="438"
        :tag-id="checkValves['1217-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
  </g>
</template>
