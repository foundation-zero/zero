<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { useAutomaticMode } from "@/modules/thrapp/state";
import { FieldEditor } from "../../editors";
import { injectValueForm } from "../../providers/forms";

const automaticMode = useAutomaticMode();
const form = injectValueForm();
</script>

<template>
  <TooltipListItem v-if="!automaticMode">
    <TooltipListItemTitle :class="{ 'text-destructive text-xs': !!form?.error }">
      {{ form?.error }}
    </TooltipListItemTitle>
    <FieldEditor.Submit />
  </TooltipListItem>
</template>
