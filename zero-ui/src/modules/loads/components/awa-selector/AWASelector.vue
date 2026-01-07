<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import SelectTriggerLabel from "@/components/ui/select/SelectTriggerLabel.vue";
import { cn, tScoped } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { AWA_VALUES } from "../../lib/consts";
import { NumRangeId } from "../../types";

const t = tScoped("loads.components.awaSelector");

const props = defineProps<{ class?: HTMLAttributes["class"] }>();

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
        v-for="item in AWA_VALUES"
        :key="item.from"
        :value="item.id"
        >{{ item.from }} - {{ item.to }}&deg;</SelectItem
      >
    </SelectContent>
  </Select>
</template>
