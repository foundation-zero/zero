<script setup lang="ts">
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { tScoped } from "@/modules/common/lib/utils";
import type { TupleIndices } from "@/modules/common/types";
import { FieldEditor } from "@/modules/thrapp/mimics/editors";
import { getMimicDataProvider, ParameterValueForm } from "@/modules/thrapp/mimics/providers";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import type { PidControllerTuning } from "@/modules/thrapp/parameters";
import type { PID } from "@/modules/thrsim/types";
import { computed } from "vue";

const t = tScoped("thrapp.parameters.pid");
const props = defineProps<PidControllerTuning>();

const { getControllerState } = getMimicDataProvider();
const controllerState = getControllerState(props.controller);
const partLabels = computed<Record<TupleIndices<PID>, string>>(() => ({
  0: t("parts.proportional"),
  1: t("parts.integral"),
  2: t("parts.derivative"),
}));
const parts: TupleIndices<PID>[] = [0, 1, 2];
</script>

<template>
  <div class="text-muted-foreground bg-dull border-border rounded-xs border">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead class="text-foreground font-medium">{{ t("table.tuning") }}</TableHead>
          <TableHead class="w-38 border-l text-center">
            {{ t("table.actual") }}
            <small class="font-light">{{ t("table.actualDescription") }}</small>
          </TableHead>
          <TableHead class="border-l text-center">{{ t("table.coefficient") }}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <ParameterValueForm :source="parameter">
          <TableRow
            v-for="part in parts"
            :key="part"
          >
            <TableCell class="py-2 pl-2">{{ partLabels[part] }}</TableCell>
            <TableCell class="border-l py-2 pl-2 text-center">
              <FieldRenderer.Number
                :transform="transform"
                :value="controllerState?.components.value[part]"
              />
            </TableCell>
            <TableCell class="w-34 p-0">
              <FieldEditor.PidTuning
                class="w-full border-l **:data-[slot=input]:border-0"
                :part="part"
              />
            </TableCell>
          </TableRow>
        </ParameterValueForm>
      </TableBody>
    </Table>
  </div>
</template>
