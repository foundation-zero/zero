<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters";
import DcFlowSettings from "./sections/DcFlowSettings.vue";
import DcPidTuning from "./sections/DcPidTuning.vue";
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

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <DcPidTuning />
  </Parameters.Pid>
</template>
