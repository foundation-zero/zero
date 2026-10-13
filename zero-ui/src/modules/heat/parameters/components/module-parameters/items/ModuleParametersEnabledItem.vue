<script setup lang="ts">
import { FieldEditor } from "@/modules/heat/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/heat/mimics/providers";
import { FieldRenderer } from "@/modules/heat/mimics/renderers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "..";

defineProps<{ source: ModuleField<ParametersType.Enabled> }>();
</script>

<template>
  <ParameterValueForm :source="source">
    <Parameters.ListItem :source="source">
      <Parameters.ListItemTitle>
        <slot />
      </Parameters.ListItemTitle>
      <Parameters.ListItemValue>
        <FieldEditor.Toggle>
          <FieldEditor.PendingIndicator />
          <FieldRenderer.EnabledDisabled />
        </FieldEditor.Toggle>
      </Parameters.ListItemValue>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
