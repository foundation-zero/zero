<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/heat-system/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/heat-system/mimics/providers";
import { FieldRenderer } from "@/modules/heat-system/mimics/renderers";
import { ParametersType } from "@/modules/heat-system-simulation/types";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.Duration> }>();
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
        {{ quantities("duration") }}
        <Parameters.Unit>{{ units("seconds") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.Duration>
        <FieldRenderer.Number />
      </FieldEditor.Duration>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
