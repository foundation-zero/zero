<script setup lang="ts">
import { Button } from "@components/shadcn/button";
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from "@components/shadcn/number-field";
import { ResponsivePopup } from "@components/shared/responsive-dialog";

import { Settings } from "lucide-vue-next";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const value = ref(400);
const open = ref(false);

const save = () => (open.value = false);
</script>

<template>
  <ResponsivePopup
    v-model:open="open"
    :title="t('views.co2Settings.title')"
    :description="t('views.co2Settings.description')"
  >
    <template #trigger>
      <button>
        <Settings />
      </button>
    </template>

    <div class="max-md:p-4">
      <NumberField
        v-model="value"
        class="my-12"
        :default-value="400"
        :step="50"
        :min="400"
        :max="1000"
      >
        <NumberFieldContent>
          <NumberFieldDecrement />
          <NumberFieldInput class="text-xl" />
          <NumberFieldIncrement />
        </NumberFieldContent>
      </NumberField>

      <Button
        class="mt-4 block w-full text-base"
        size="lg"
        @click="save"
        >{{ t("labels.save") }}</Button
      >
    </div>
  </ResponsivePopup>
</template>
