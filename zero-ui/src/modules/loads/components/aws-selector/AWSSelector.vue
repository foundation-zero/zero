<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectTriggerLabel,
  SelectValue,
} from "@/components/ui/select";
import { cn, tScoped } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { AWS_VALUES } from "../../lib/consts";
import { NumRangeId } from "../../types";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const t = tScoped("loads.components.awsSelector");

const modelValue = defineModel<NumRangeId>({
  required: true,
});
</script>

<template>
  <Select v-model:model-value="modelValue">
    <SelectTrigger :class="cn('h-10', props.class)">
      <SelectTriggerLabel>{{ t("label") }}</SelectTriggerLabel>
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem
        v-for="item in AWS_VALUES"
        :key="item.from"
        :value="item.id"
      >
        <template v-if="item.to === Infinity">{{ item.from }}+</template>
        <template v-else>{{ item.from }} - {{ item.to }} {{ t("unit") }}</template>
      </SelectItem>
    </SelectContent>
  </Select>
</template>
