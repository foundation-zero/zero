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
    <Parameters.CardTitle>{{ t("consumersBoosting.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("consumersBoosting.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled :source="getField(ParametersType.Enabled, 'consumers', 'dhwEnabled')">
        {{ t("items.domesticHotWater") }}
      </ParameterItems.Enabled>
      <ParameterItems.FlowRatio
        :source="getField(ParametersType.Flow, 'consumers', 'dhwFlowRatioSetpoint')"
      >
        {{ t("items.flowRatioToCircuit") }}
      </ParameterItems.FlowRatio>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'consumers', 'adsorptionEnabled')"
      >
        {{ t("items.adsorption") }}
      </ParameterItems.Enabled>
      <ParameterItems.FlowRatio
        :source="getField(ParametersType.Flow, 'consumers', 'adsorptionFlowRatioSetpoint')"
      >
        {{ t("items.flowRatioToCircuit") }}
      </ParameterItems.FlowRatio>
    </Parameters.List>
  </Parameters.Card>
</template>
