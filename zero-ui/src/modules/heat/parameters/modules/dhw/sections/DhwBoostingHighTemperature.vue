<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/heat/mimics/providers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("heat.parameters.dhw");
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
