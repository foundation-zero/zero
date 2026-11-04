<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/thrapp/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/thrapp/mimics/providers";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { ParametersType } from "@/modules/thrapp/types/thrs";
import { SimpleInfoTooltip } from "@/modules/common/components/info-tooltip";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.FlowControl> }>();
</script>

<template>
  <ParameterValueForm :source="source">
    <Parameters.ListItem
      multiline
      :source="source"
    >
      <Parameters.ListItemTitle>
        <slot />
        <SimpleInfoTooltip :description="source[2]" />
      </Parameters.ListItemTitle>
      <Parameters.Quantity>
        {{ quantities("position") }}
        <Parameters.Unit>{{ units("percent") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.Percentage>
        <FieldRenderer.Percentage />
      </FieldEditor.Percentage>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
