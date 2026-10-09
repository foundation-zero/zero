<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("thrapp.parameters.pcm");
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
