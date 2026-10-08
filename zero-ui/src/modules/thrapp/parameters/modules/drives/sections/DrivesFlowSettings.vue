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
    <Parameters.CardTitle>{{ t("flowSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("flowSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Flow
        :source="getField(ParametersType.Flow, 'drives', 'shorepowerFlowSetpoint')"
      >
        {{ t("items.shorepowerFlowSetpoint") }}
      </ParameterItems.Flow>
      <ParameterItems.Flow
        :source="getField(ParametersType.Flow, 'drives', 'propulsionDrivesFlowSetpoint')"
      >
        {{ t("items.propulsionDrivesFlowSetpoint") }}
      </ParameterItems.Flow>
    </Parameters.List>
  </Parameters.Card>
</template>
