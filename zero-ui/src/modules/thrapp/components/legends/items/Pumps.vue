<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentState } from "@/modules/thrapp/mimics/components";
import { PumpState } from "../../../mimics/components/pump";
import Pump from "../../../mimics/components/pump/Pump.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.pumps");
</script>

<template>
  <LegendItem>
    <LegendItemPreview class="-my-2">
      <Pump
        :pump-state="PumpState.Active"
        class="-ml-2"
      />
      <Pump :pump-state="PumpState.Inactive" />
      <Pump :pump-state="MimicComponentState.Alarm" />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
