<script setup lang="ts">
import { ZiPlug3 } from "@/modules/common/components/icons";
import { MimicComponentType } from "@/modules/thrapp/types";
import { DcConverterInstance } from "../../../instances";
import { DRIVES_ASSET_DATA } from "../data";

const converters = DRIVES_ASSET_DATA[MimicComponentType.DcConverter];
</script>

<template>
  <DcConverterInstance
    x="881.1582"
    y="20.916"
    :height="222"
    v-bind="converters.shorepower"
  >
    <template #icon>
      <ZiPlug3 class="size-10" />
    </template>
  </DcConverterInstance>
</template>
