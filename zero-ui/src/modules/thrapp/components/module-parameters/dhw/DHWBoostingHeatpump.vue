<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrs/types";
import * as Parameters from "..";
import * as ParameterItems from "../items";

const t = tScoped("thrapp.parameters.dhw");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("boostingHeatpump.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("boostingHeatpump.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'dhw', 'heatpumpTemperatureSetpoint')"
      >
        {{ t("items.heatpumpTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'dhw', 'heatpumpFlowSetpoint')">
        {{ t("items.heatpumpFlow") }}
      </ParameterItems.Flow>
    </Parameters.List>
  </Parameters.Card>
</template>
