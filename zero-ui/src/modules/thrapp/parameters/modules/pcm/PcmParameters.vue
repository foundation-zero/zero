<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import PcmChargingSettings from "./sections/PcmChargingSettings.vue";
import PcmConsumersBoosting from "./sections/PcmConsumersBoosting.vue";
import PcmFlowSettings from "./sections/PcmFlowSettings.vue";
import PcmPidTuning from "./sections/PcmPidTuning.vue";
import PcmStallGuardSettings from "./sections/PcmStallGuardSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("pcm.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <PcmChargingSettings />
    <PcmFlowSettings />
    <PcmConsumersBoosting />
    <PcmStallGuardSettings />
  </Parameters.Root>

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <PcmPidTuning />
  </Parameters.Pid>
</template>
