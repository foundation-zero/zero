<script setup lang="ts">
import { DcConverterStatusProps } from ".";
import SensorValue from "../../providers/SensorValue.vue";

defineProps<DcConverterStatusProps>();
</script>

<template>
  <ul class="flex grow-0 gap-1">
    <SensorValue
      v-for="(source, index) in sources"
      :key="index"
      :source="source"
      field="active"
    >
      <template #default="{ value }">
        <li
          class="size-3"
          :class="{ 'bg-constructive': value, 'bg-muted': !value }"
        />
      </template>
    </SensorValue>
  </ul>
</template>
