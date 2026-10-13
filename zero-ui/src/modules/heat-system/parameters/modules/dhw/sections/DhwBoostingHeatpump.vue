<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/heat-system/mimics/providers";
import { ParametersType } from "@/modules/heat-system-simulation/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("heatSystem.parameters.dhw");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("boostingHeatpump.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("boostingHeatpump.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'dhw', 'heatpumpBoostingEnabled')"
      >
        {{ t("items.heatpumpBoosting") }}
      </ParameterItems.Enabled>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'dhw', 'heatpumpFlowSetpoint')">
        {{ t("items.heatpumpFlow") }}
      </ParameterItems.Flow>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'dhw', 'heatpumpTemperatureSetpoint')"
      >
        {{ t("items.heatpumpTemperature") }}
      </ParameterItems.Temperature>
    </Parameters.List>
  </Parameters.Card>
</template>
