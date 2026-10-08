<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import PvtPumpControl from "./sections/PvtPumpControl.vue";
import PvtTemperatureSettings from "./sections/PvtTemperatureSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("pvt.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <PvtTemperatureSettings />
    <PvtPumpControl />
  </Parameters.Root>
</template>
