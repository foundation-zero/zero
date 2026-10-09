<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import {
  TooltipList,
  TooltipListItem,
  TooltipListItemTitle,
} from "@/modules/thrapp/components/tooltip-list";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import ControllerStateValue from "@/modules/thrapp/mimics/providers/ControllerStateValue.vue";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { PidControllerTuning } from "../..";
import * as Partials from "../../../mimics/tooltips/partials";
import * as Parameters from "../../components/module-parameters";
import PidTuningTable from "../../components/pid-tuning-table/PidTuningTable.vue";
const t = tScoped("thrapp.parameters.pid");

const props = defineProps<PidControllerTuning>();
</script>

<template>
  <NoopTooltipProvider>
    <Parameters.Card>
      <Parameters.CardTitle class="flex items-center justify-between">
        {{ t(`${controller[2]}.title`) }}
        <ControllerStateValue
          :source="props.controller"
          field="enabled"
        >
          <FieldRenderer.HeatPumpMode />
        </ControllerStateValue>
      </Parameters.CardTitle>
      <Parameters.Description>{{ t(`${controller[2]}.description`) }}</Parameters.Description>
      <Parameters.Separator />
      <TooltipList class="border-0">
        <Partials.PIDController
          no-source
          v-bind="props"
        >
          <template #header>
            <TooltipListItem>
              <TooltipListItemTitle>{{ t("components") }}</TooltipListItemTitle>
            </TooltipListItem>
          </template>
        </Partials.PIDController>
      </TooltipList>

      <TooltipListItemTitle>{{ t("configuration") }}</TooltipListItemTitle>
      <PidTuningTable v-bind="props" />
    </Parameters.Card>
  </NoopTooltipProvider>
</template>
