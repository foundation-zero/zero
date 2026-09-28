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
    <Parameters.CardTitle>{{ t("boostingModeSelection.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("boostingModeSelection.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'dhw', 'minimumTankTemperature')"
      >
        {{ t("items.minimumTankTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'dhw', 'maximumTankTemperature')"
      >
        {{ t("items.maximumTankTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.Dutypoint
        :source="getField(ParametersType.Dutypoint, 'dhw', 'minimumPumpDutypoint')"
      >
        {{ t("items.minimumPumpDutypoint") }}
      </ParameterItems.Dutypoint>
      <ParameterItems.Power :source="getField(ParametersType.Power, 'dhw', 'boostingMinimumHeat')">
        {{ t("items.boostingMinimumHeat") }}
      </ParameterItems.Power>
      <ParameterItems.Duration
        :source="getField(ParametersType.Duration, 'dhw', 'boostingStartupGrace')"
      >
        {{ t("items.boostingStartupGrace") }}
      </ParameterItems.Duration>
      <ParameterItems.Duration
        :source="getField(ParametersType.Duration, 'dhw', 'boostingStallWindow')"
      >
        {{ t("items.boostingStallWindow") }}
      </ParameterItems.Duration>
      <ParameterItems.Duration
        :source="getField(ParametersType.Duration, 'dhw', 'boostingStallCooldown')"
      >
        {{ t("items.boostingStallCooldown") }}
      </ParameterItems.Duration>
    </Parameters.List>
  </Parameters.Card>
</template>
