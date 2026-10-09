<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import DhwBoostingHeatpump from "./sections/DhwBoostingHeatpump.vue";
import DhwBoostingHighTemperature from "./sections/DhwBoostingHighTemperature.vue";
import DhwBoostingModeSelection from "./sections/DhwBoostingModeSelection.vue";
import DhwFillingParameters from "./sections/DhwFillingParameters.vue";
import DhwPidTuning from "./sections/DhwPidTuning.vue";
import DhwTankSelection from "./sections/DhwTankSelection.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("dhw.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <DhwTankSelection />
    <DhwFillingParameters />
    <DhwBoostingModeSelection />
    <DhwBoostingHeatpump />
    <DhwBoostingHighTemperature />
  </Parameters.Root>

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <DhwPidTuning />
  </Parameters.Pid>
</template>
