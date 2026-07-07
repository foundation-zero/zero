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
    <Parameters.CardTitle>{{ t("tankSelection.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("tankSelection.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Enabled :source="getField(ParametersType.Disabled, 'dhw', 'tank1Disabled')">
        {{ t("items.tank1") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled :source="getField(ParametersType.Disabled, 'dhw', 'tank2Disabled')">
        {{ t("items.tank2") }}
      </ParameterItems.Enabled>
      <ParameterItems.Enabled :source="getField(ParametersType.Disabled, 'dhw', 'tank3Disabled')">
        {{ t("items.tank3") }}
      </ParameterItems.Enabled>
    </Parameters.List>
  </Parameters.Card>
</template>
