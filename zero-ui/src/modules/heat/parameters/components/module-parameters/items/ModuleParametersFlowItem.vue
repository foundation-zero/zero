<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/heat/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/heat/mimics/providers";
import { FieldRenderer } from "@/modules/heat/mimics/renderers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.Flow> }>();
</script>

<template>
  <ParameterValueForm :source="source">
    <Parameters.ListItem
      multiline
      :source="source"
    >
      <Parameters.ListItemTitle>
        <slot />
      </Parameters.ListItemTitle>
      <Parameters.Quantity>
        {{ quantities("flow") }}
        <Parameters.Unit>{{ units("lpm") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.FlowRate>
        <FieldRenderer.FlowRate />
      </FieldEditor.FlowRate>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
