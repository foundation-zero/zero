<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import SwitchValve from "@/modules/thrapp/mimics/components/actuated-valve/SwitchValve.vue";
import TwoWayValve from "@/modules/thrapp/mimics/components/actuated-valve/TwoWayValve.vue";
import ActuatedValve from "../../../mimics/components/actuated-valve/ActuatedValve.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend/index.ts";

const t = tScoped("thrapp.legends.switchValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ActuatedValve>
        <SwitchValve />
        <TwoWayValve :flow="1" />
      </ActuatedValve>
      <ActuatedValve :rotation="0.5">
        <SwitchValve />
        <TwoWayValve :flow="0.5" />
      </ActuatedValve>
      <ActuatedValve :rotation="1">
        <SwitchValve />
        <TwoWayValve :flow="0" />
      </ActuatedValve>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
