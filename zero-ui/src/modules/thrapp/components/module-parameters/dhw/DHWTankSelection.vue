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
    <Parameters.CardTitle>{{ t("tankSelection.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("tankSelection.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled :source="getField(ParametersType.Enabled, 'dhw', 'tank1Enabled')">
        {{ t("items.tank1") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled :source="getField(ParametersType.Enabled, 'dhw', 'tank2Enabled')">
        {{ t("items.tank2") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled :source="getField(ParametersType.Enabled, 'dhw', 'tank3Enabled')">
        {{ t("items.tank3") }}
      </ParameterItems.Enabled>
    </Parameters.List>
  </Parameters.Card>
</template>
