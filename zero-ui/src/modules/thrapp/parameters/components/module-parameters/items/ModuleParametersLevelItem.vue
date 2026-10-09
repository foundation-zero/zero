<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/thrapp/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/thrapp/mimics/providers";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { ParametersType } from "@/modules/thrsim/types";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.Level> }>();
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
        {{ quantities("liter") }}
        <Parameters.Unit>{{ units("liters") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.TankLevel>
        <FieldRenderer.Level />
      </FieldEditor.TankLevel>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
