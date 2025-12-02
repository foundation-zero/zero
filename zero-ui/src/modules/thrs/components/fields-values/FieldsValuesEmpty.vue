<script setup lang="ts">
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { tScoped } from "@/modules/common/lib/utils";
import { FilterX } from "lucide-vue-next";
import { getContext } from ".";

const t = tScoped("thrs.components.fieldsValues.empty");
const { selected } = getContext();
</script>

<template>
  <Empty
    v-if="!selected.length"
    class="col-span-full border"
  >
    <EmptyHeader>
      <EmptyMedia variant="icon">
        <FilterX />
      </EmptyMedia>
    </EmptyHeader>
    <EmptyTitle>{{ t("title") }}</EmptyTitle>
    <EmptyDescription>{{ t("description") }}</EmptyDescription>
  </Empty>
</template>
