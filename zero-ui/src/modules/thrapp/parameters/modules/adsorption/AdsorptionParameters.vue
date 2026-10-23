<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters";
import AdsorptionPidTuning from "./sections/AdsorptionPidTuning.vue";
import AdsorptionSettings from "./sections/AdsorptionSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("adsorption.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <AdsorptionSettings />
  </Parameters.Root>

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <AdsorptionPidTuning />
  </Parameters.Pid>
</template>
