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
    <Parameters.CardTitle>{{ t("flowSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("flowSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'pcm', 'pcmChargeFlow')">
        {{ t("items.pcmChargeFlow") }}
      </ParameterItems.Flow>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'pcm', 'pcmDischargeFlow')">
        {{ t("items.pcmDischargeFlow") }}
      </ParameterItems.Flow>
    </Parameters.List>
  </Parameters.Card>
</template>
