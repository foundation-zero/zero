<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import MixValve from "@/modules/thrapp/mimics/components/actuated-valve/MixValve.vue";
import TwoWayValve from "@/modules/thrapp/mimics/components/actuated-valve/TwoWayValve.vue";
import ActuatedValve from "../../../mimics/components/actuated-valve/ActuatedValve.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.flowValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ActuatedValve>
        <MixValve />
        <TwoWayValve :flow="1" />
      </ActuatedValve>
      <ActuatedValve>
        <TwoWayValve :flow="0.5" />
        <MixValve />
      </ActuatedValve>
      <ActuatedValve>
        <MixValve />
        <TwoWayValve :flow="0" />
      </ActuatedValve>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
