<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { ActuatedValveType, FlowValveState } from "../../../mimics/components/actuated-valve";
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
      <ActuatedValve
        :type="ActuatedValveType.FlowControl"
        :state="FlowValveState.Open"
      />
      <ActuatedValve
        :type="ActuatedValveType.FlowControl"
        :state="FlowValveState.Partial"
      />
      <ActuatedValve
        :type="ActuatedValveType.FlowControl"
        :state="FlowValveState.Closed"
      />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
