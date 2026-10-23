<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import ActuatedValve from "@/modules/thrapp/mimics/components/actuated-valve/ActuatedValve.vue";
import MixValve from "@/modules/thrapp/mimics/components/actuated-valve/MixValve.vue";
import ThreeWayValve from "@/modules/thrapp/mimics/components/actuated-valve/ThreeWayValve.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.threeWayMixValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ActuatedValve>
        <MixValve />
        <ThreeWayValve :flow="1" />
      </ActuatedValve>
      <ActuatedValve>
        <MixValve />
        <ThreeWayValve :flow="0" />
      </ActuatedValve>
      <ActuatedValve>
        <MixValve />
        <ThreeWayValve :flow="0.5" />
      </ActuatedValve>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
