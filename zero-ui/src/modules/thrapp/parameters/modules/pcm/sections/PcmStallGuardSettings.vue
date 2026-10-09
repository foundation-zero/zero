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
    <Parameters.CardTitle>{{ t("stallGuardSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("stallGuardSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Duration :source="getField(ParametersType.Duration, 'pcm', 'gracePeriod')">
        {{ t("items.gracePeriod") }}
      </ParameterItems.Duration>
      <ParameterItems.Duration :source="getField(ParametersType.Duration, 'pcm', 'stallDuration')">
        {{ t("items.stallDuration") }}
      </ParameterItems.Duration>
      <ParameterItems.Duration :source="getField(ParametersType.Duration, 'pcm', 'retryDelay')">
        {{ t("items.retryDelay") }}
      </ParameterItems.Duration>
    </Parameters.List>
  </Parameters.Card>
</template>
