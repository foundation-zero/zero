<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import {
  TooltipList,
  TooltipListItem,
  TooltipListItemTitle,
} from "@/modules/thrapp/components/tooltip-list";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import { SensorGraph } from "@/modules/thrapp/mimics/components/sensor-graph";
import ControllerStateValue from "@/modules/thrapp/mimics/providers/ControllerStateValue.vue";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { useTranslations } from "@/modules/thrapp/mimics/tooltips";
import { kebabCase } from "lodash";
import { PidControllerTuning } from "../..";
import * as Partials from "../../../mimics/tooltips/partials";
import * as Parameters from "../../components/module-parameters";
import PidTuningTable from "../../components/pid-tuning-table/PidTuningTable.vue";
const t = tScoped("thrapp.parameters.pid");

const props = defineProps<PidControllerTuning>();

const { sources } = useTranslations();
</script>

<template>
  <NoopTooltipProvider>
    <Parameters.Card>
      <hgroup class="flex items-baseline justify-between">
        <Parameters.CardTitle>
          {{ sources(`${controller[0]}.${controller[2]}`) }}
        </Parameters.CardTitle>
        <ControllerStateValue
          :source="props.controller"
          field="enabled"
        >
          <FieldRenderer.HeatPumpMode icon />
        </ControllerStateValue>
      </hgroup>

      <Parameters.Description>{{ t(`${controller[2]}.description`) }}</Parameters.Description>
      <Parameters.Separator />
      <TooltipList class="border-0">
        <Partials.PIDController v-bind="{ controller, type }">
          <template #header>
            <TooltipListItem>
              <TooltipListItemTitle>{{ t("components") }}</TooltipListItemTitle>
            </TooltipListItem>
          </template>
        </Partials.PIDController>
      </TooltipList>

      <TooltipListItemTitle>{{ t("configuration") }}</TooltipListItemTitle>
      <PidTuningTable v-bind="props" />
      <TooltipListItemTitle>{{ t("graph") }}</TooltipListItemTitle>
      <SensorGraph
        :device="kebabCase(props.controller[2])"
        type="pid_controllers"
        :field="['measurement', 'target', 'error', 'output']"
      />
    </Parameters.Card>
  </NoopTooltipProvider>
</template>
