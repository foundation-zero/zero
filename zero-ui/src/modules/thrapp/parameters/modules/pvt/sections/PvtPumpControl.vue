<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "../../../components/module-parameters";
import * as ParameterItems from "../../../components/module-parameters/items";

const t = tScoped("thrapp.parameters.pvt");
</script>

<template>
  <Parameters.Card>
    <Parameters.CardTitle>{{ t("pumpControl.title") }}</Parameters.CardTitle>
    <Parameters.Description>{{ t("pumpControl.description") }}</Parameters.Description>
    <Parameters.Separator />
    <Parameters.List>
      <ParameterItems.Dutypoint
        :source="getField(ParametersType.Dutypoint, 'pvt', 'mainFwdMinimumPumpDutypoint')"
      >
        {{ t("items.mainFwdMinimumPumpDutypoint") }}
      </ParameterItems.Dutypoint>
      <ParameterItems.Dutypoint
        :source="getField(ParametersType.Dutypoint, 'pvt', 'mainAftMinimumPumpDutypoint')"
      >
        {{ t("items.mainAftMinimumPumpDutypoint") }}
      </ParameterItems.Dutypoint>
      <ParameterItems.Dutypoint
        :source="getField(ParametersType.Dutypoint, 'pvt', 'ownersMinimumPumpDutypoint')"
      >
        {{ t("items.ownersMinimumPumpDutypoint") }}
      </ParameterItems.Dutypoint>
    </Parameters.List>
  </Parameters.Card>
</template>
