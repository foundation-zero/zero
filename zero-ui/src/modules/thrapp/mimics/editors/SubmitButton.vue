<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { RiLoader2Line, RiSendPlaneLine } from "@remixicon/vue";
import { injectControlValueForm } from "../providers/forms";
import { useTranslations } from "../tooltips";

const form = injectControlValueForm();
const { actions } = useTranslations();
</script>

<template>
  <Button
    v-if="form?.editable.value"
    :disabled="!form?.isDirty.value || form?.isPending.value"
    size="sm"
    @click="form?.submit()"
  >
    <RiLoader2Line
      v-if="form?.isPending.value"
      class="animate-spin"
    />
    <RiSendPlaneLine v-else />
    {{ actions("confirm") }}
  </Button>
</template>
