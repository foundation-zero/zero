<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("thrapp.parameters.drives");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("temperatureSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("temperatureSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'drives', 'recoveryTemperature')"
      >
        {{ t("items.recoveryTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="
          getField(ParametersType.Temperature, 'drives', 'shorepowerMaximumSupplyTemperature')
        "
      >
        {{ t("items.shorepowerMaximumSupplyTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.Temperature
        :source="
          getField(ParametersType.Temperature, 'drives', 'propulsionMaximumSupplyTemperature')
        "
      >
        {{ t("items.propulsionMaximumSupplyTemperature") }}
      </ParameterItems.Temperature>
    </Parameters.List>
  </Parameters.Card>
</template>
