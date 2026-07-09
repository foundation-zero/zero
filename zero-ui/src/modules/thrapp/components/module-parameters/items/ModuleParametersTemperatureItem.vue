<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { FieldEditor } from "@/modules/thrapp/mimics/editors";
import { ModuleField, ParameterValueForm } from "@/modules/thrapp/mimics/providers";
import { FieldRenderer } from "@/modules/thrapp/mimics/renderers";
import { ParametersType } from "@/modules/thrs/types";
import * as Parameters from "..";

const quantities = tScoped("quantities");
const units = tScoped("units");

defineProps<{ source: ModuleField<ParametersType.Temperature | ParametersType.dT> }>();
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
        {{ quantities("temperature") }}
        <Parameters.Unit>{{ units("celsius") }}</Parameters.Unit>
      </Parameters.Quantity>
      <FieldEditor.Temperature>
        <FieldRenderer.Temperature />
      </FieldEditor.Temperature>
    </Parameters.ListItem>
  </ParameterValueForm>
</template>
