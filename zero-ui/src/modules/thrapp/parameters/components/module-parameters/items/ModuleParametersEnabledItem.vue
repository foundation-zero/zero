<script setup lang="ts">
import { FieldEditor } from "@/modules/thrapp/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/thrapp/mimics/providers";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { ParametersType } from "@/modules/thrapp/types/thrs";
import { SimpleInfoTooltip } from "@/modules/common/components/info-tooltip";
import * as Parameters from "..";

defineProps<{ source: ModuleField<ParametersType.Enabled> }>();
</script>

<template>
  <ParameterValueForm :source="source">
    <Parameters.ListItem :source="source">
      <Parameters.ListItemTitle>
        <slot />
        <SimpleInfoTooltip :description="source[2]" />
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
