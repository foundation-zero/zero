<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import SelectTriggerLabel from "@/components/ui/select/SelectTriggerLabel.vue";
import { tScoped } from "@/modules/common/lib/utils";
import { TWA_VALUES } from "../../lib/consts";

const t = tScoped("loads.components.twaSelector");

const modelValue = defineModel<number>({
  type: [Number],
  required: true,
});
</script>

<template>
  <Select v-model:model-value="modelValue">
    <SelectTrigger class="w-[16.375rem]">
      <SelectTriggerLabel>{{ t("label") }}</SelectTriggerLabel>
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="item in TWA_VALUES"
        :key="item.from"
        :value="item.id"
        >{{ item.from }} - {{ item.to }}&deg;</SelectItem
      >
    </SelectContent>
  </Select>
</template>
