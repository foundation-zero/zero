<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import ThrustersFlowSettings from "./sections/ThrustersFlowSettings.vue";
import ThrustersPidTuning from "./sections/ThrustersPidTuning.vue";
import ThrustersTemperatureSettings from "./sections/ThrustersTemperatureSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("thrusters.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <ThrustersTemperatureSettings />
    <ThrustersFlowSettings />
  </Parameters.Root>

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <ThrustersPidTuning />
  </Parameters.Pid>
</template>
