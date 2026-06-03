<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { ActuatedValveType, SwitchValveState } from "../../../mimics/components/actuated-valve";
import ActuatedValve from "../../../mimics/components/actuated-valve/ActuatedValve.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.switchValve");
</script>

<template>
  <LegendItem>
    <LegendItemPreview>
      <ActuatedValve
        :type="ActuatedValveType.Switch"
        :state="SwitchValveState.Open"
      />
      <ActuatedValve
        :type="ActuatedValveType.Switch"
        :state="SwitchValveState.Closed"
      />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
