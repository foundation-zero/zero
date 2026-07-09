<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrs/types";
import * as Parameters from "..";
import * as ParameterItems from "../items";

const t = tScoped("thrapp.parameters.dhw");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("fillingParameters.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("fillingParameters.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Level :source="getField(ParametersType.Level, 'dhw', 'minimumTankLevel')">
        {{ t("items.minimumTankLevel") }}
      </ParameterItems.Level>
      <ParameterItems.Level :source="getField(ParametersType.Level, 'dhw', 'maximumTankLevel')">
        {{ t("items.maximumTankLevel") }}
      </ParameterItems.Level>
      <ParameterItems.Temperature
        :source="getField(ParametersType.Temperature, 'dhw', 'fillingTemperatureSetpoint')"
      >
        {{ t("items.fillingTemperature") }}
      </ParameterItems.Temperature>
      <ParameterItems.FlowControl
        :source="getField(ParametersType.FlowControl, 'dhw', 'drivesFlowcontrolMinimumSetpoint')"
      >
        {{ t("items.minimumFlowDrives") }}
      </ParameterItems.FlowControl>
      <ParameterItems.FlowControl
        :source="getField(ParametersType.FlowControl, 'dhw', 'dcFlowcontrolMinimumSetpoint')"
      >
        {{ t("items.minimumFlowDC") }}
      </ParameterItems.FlowControl>
    </Parameters.List>
  </Parameters.Card>
</template>
