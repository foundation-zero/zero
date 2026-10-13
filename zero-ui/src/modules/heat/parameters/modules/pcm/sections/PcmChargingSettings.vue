<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/heat/mimics/providers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("heat.parameters.pcm");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("chargingSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("chargingSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'pcm', 'supplyingRequested')"
      >
        {{ t("items.supplyingRequested") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'pcm', 'chargingRequested')"
      >
        {{ t("items.chargingRequested") }}
      </ParameterItems.Enabled>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'pcm', 'minimumChargingTemperature')"
      >
        {{ t("items.minimumChargingTemperature") }}
      </ParameterItems.Temperature>
    </Parameters.List>
  </Parameters.Card>
</template>
