<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import DcFlowSettings from "./sections/DcFlowSettings.vue";
import DcTemperatureSettings from "./sections/DcTemperatureSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("dc.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <DcTemperatureSettings />
    <DcFlowSettings />
  </Parameters.Root>
</template>
