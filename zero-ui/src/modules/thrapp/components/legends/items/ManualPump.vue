<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { MimicComponentState } from "@/modules/thrapp/mimics/components";
import { PumpState } from "@/modules/thrapp/mimics/components/pump";
import Pump from "@/modules/thrapp/mimics/components/pump/Pump.vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const t = tScoped("thrapp.legends.manualPump");
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <Pump
        :pump-state="PumpState.Inactive"
        :state="MimicComponentState.Manual"
        manual
      />
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
