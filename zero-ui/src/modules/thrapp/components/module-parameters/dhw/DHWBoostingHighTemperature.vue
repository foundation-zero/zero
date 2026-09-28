<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "..";
import * as ParameterItems from "../items";

const t = tScoped("thrapp.parameters.dhw");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("boostingHighTemperature.title") }}</Parameters.CardTitle>
    <Parameters.Description>
      {{ t("boostingHighTemperature.description") }}
    </Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'dhw', 'htBoostingEnabled')"
      >
        {{ t("items.highTemperatureBoosting") }}
      </ParameterItems.Enabled>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'dhw', 'htBoostingFlowSetpoint')">
        {{ t("items.boostingFlow") }}
      </ParameterItems.Flow>
      <ParameterItems.Temperature
        :source="getField(ParametersType.dT, 'dhw', 'htBoostingMinimumDelta')"
      >
        {{ t("items.htBoostingMinimumDelta") }}
      </ParameterItems.Temperature>
    </Parameters.List>
  </Parameters.Card>
</template>
