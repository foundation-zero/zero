<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/heat/mimics/providers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("heat.parameters.adsorption");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("settings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("settings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'adsorption', 'chillerEnabled')"
      >
        {{ t("items.chillerEnabled") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled
        :source="getField(ParametersType.Enabled, 'adsorption', 'freeCoolingEnabled')"
      >
        {{ t("items.freeCoolingEnabled") }}
      </ParameterItems.Enabled>
      <ParameterItems.Temperature
        :source="
          getField(ParametersType.Temperature, 'adsorption', 'wasteCoolingTemperatureSetpoint')
        "
      >
        {{ t("items.wasteCoolingTemperatureSetpoint") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="
          getField(ParametersType.Temperature, 'adsorption', 'wasteRecoveryTemperatureSetpoint')
        "
      >
        {{ t("items.wasteRecoveryTemperatureSetpoint") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'hotSupplyTemperatureSetpoint')"
      >
        {{ t("items.hotSupplyTemperatureSetpoint") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'adsorptionCoolingSetpoint')"
      >
        {{ t("items.adsorptionCoolingSetpoint") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'adsorptionHotMinimum')"
      >
        {{ t("items.adsorptionHotMinimum") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'adsorptionHotTrigger')"
      >
        {{ t("items.adsorptionHotTrigger") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'adsorptionColdMinimum')"
      >
        {{ t("items.adsorptionColdMinimum") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'adsorption', 'adsorptionColdTrigger')"
      >
        {{ t("items.adsorptionColdTrigger") }}
      </ParameterItems.Temperature>
    </Parameters.List>
  </Parameters.Card>
</template>
