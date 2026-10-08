<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("thrapp.parameters.dc");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("flowSettings.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("flowSettings.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'dc', 'brightloopFlowSetpoint')">
        {{ t("items.brightloopFlowSetpoint") }}
      </ParameterItems.Flow>
      <ParameterItems.Flow :source="getField(ParametersType.Flow, 'dc', 'ugridFlowSetpoint')">
        {{ t("items.ugridFlowSetpoint") }}
      </ParameterItems.Flow>
    </Parameters.List>
  </Parameters.Card>
</template>
