<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils.ts";
import { ComponentOrientation, HeatingState } from "../../../mimics/components";
import { HeatExchangerPortOrientation } from "../../../mimics/components/heat-exchanger";
import HeatExchanger from "../../../mimics/components/heat-exchanger/HeatExchanger.vue";
import HeatExchangerPort from "../../../mimics/components/heat-exchanger/HeatExchangerPort.vue";
import {
  LegendItem,
  LegendItemDescription,
  LegendItemInfo,
  LegendItemPreview,
  LegendItemTitle,
} from "../../legend";

const t = tScoped("thrapp.legends.plateHeatExchanger");
</script>

<template>
  <LegendItem>
    <LegendItemPreview class="gap-3">
      <svg
        width="40"
        height="40"
        viewBox="0 0 56 56"
      >
        <HeatExchanger
          :pump-state="HeatingState.Active"
          :orientation="ComponentOrientation.Up"
        >
          <HeatExchangerPort
            side="a"
            :state="HeatingState.HeatingMedium"
            :orientation="HeatExchangerPortOrientation.Top"
          />
          <HeatExchangerPort
            side="b"
            :state="HeatingState.HeatingHigh"
            :orientation="HeatExchangerPortOrientation.Top"
          />
        </HeatExchanger>
      </svg>

      <svg
        width="40"
        height="40"
        viewBox="0 0 56 56"
      >
        <HeatExchanger
          :pump-state="HeatingState.Active"
          :orientation="ComponentOrientation.Up"
        >
          <HeatExchangerPort
            side="a"
            :state="HeatingState.CoolingHigh"
            :orientation="HeatExchangerPortOrientation.Top"
          />
          <HeatExchangerPort
            side="b"
            :state="HeatingState.CoolingMedium"
            :orientation="HeatExchangerPortOrientation.Top"
          />
        </HeatExchanger>
      </svg>

      <svg
        width="40"
        height="40"
        viewBox="0 0 56 56"
      >
        <HeatExchanger
          :pump-state="HeatingState.Active"
          :orientation="ComponentOrientation.Up"
        >
          <HeatExchangerPort
            side="a"
            :state="HeatingState.Idle"
            :orientation="HeatExchangerPortOrientation.Top"
          />
          <HeatExchangerPort
            side="b"
            :state="HeatingState.Idle"
            :orientation="HeatExchangerPortOrientation.Top"
          />
        </HeatExchanger>
      </svg>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>{{ t("title") }}</LegendItemTitle>
      <LegendItemDescription>{{ t("description") }}</LegendItemDescription>
    </LegendItemInfo>
  </LegendItem>
</template>
