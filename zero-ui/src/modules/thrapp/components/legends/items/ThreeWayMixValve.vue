<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { ActuatedValveType, ThreeWayValveState } from "../../../mimics/components/actuated-valve";
import ActuatedValve from "../../../mimics/components/actuated-valve/ActuatedValve.vue";
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
      <ActuatedValve
        :type="ActuatedValveType.ThreeWay"
        :state="ThreeWayValveState.AA"
      />
      <ActuatedValve
        :type="ActuatedValveType.ThreeWay"
        :state="ThreeWayValveState.AB"
      />
      <ActuatedValve
        :type="ActuatedValveType.ThreeWay"
        :state="ThreeWayValveState.BA"
      />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
