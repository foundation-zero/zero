<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectTriggerLabel,
  SelectValue,
} from "@/components/ui/select";
import { tScoped } from "@/modules/common/lib/utils";
import { TWS_VALUES } from "../../lib/consts";

const t = tScoped("loads.components.twsSelector");

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
        v-for="item in TWS_VALUES"
        :key="item.from"
        :value="item.id"
      >
        <template v-if="item.to === Infinity">{{ item.from }}+</template>
        <template v-else>{{ item.from }} - {{ item.to }} {{ t("unit") }}</template>
      </SelectItem>
    </SelectContent>
  </Select>
</template>
