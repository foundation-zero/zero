<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/heat/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/heat/mimics/providers";
import { FieldRenderer } from "@/modules/heat/mimics/renderers";
import { ParametersType } from "@/modules/heat-simulation/types";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.Power> }>();
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
        {{ quantities("power") }}
        <Parameters.Unit>{{ units("watts") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.Power>
        <FieldRenderer.Number />
      </FieldEditor.Power>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
