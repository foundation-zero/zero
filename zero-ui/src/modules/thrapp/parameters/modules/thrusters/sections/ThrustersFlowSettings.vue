<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("thrapp.parameters.thrusters");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("flowSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("flowSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Flow
        :source="getField(ParametersType.Flow, 'thrusters', 'thrustersMinimumFlow')"
      >
        {{ t("items.minimumFlow") }}
      </ParameterItems.Flow>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'thrusters', 'coolingFlow')">
        {{ t("items.coolingFlow") }}
      </ParameterItems.Flow>
      <ParameterItems.Flow
        :source="getField(ParametersType.Flow, 'thrusters', 'thrustersMaximumFlow')"
      >
        {{ t("items.maximumFlow") }}
      </ParameterItems.Flow>
    </Parameters.List>
  </Parameters.Card>
</template>
