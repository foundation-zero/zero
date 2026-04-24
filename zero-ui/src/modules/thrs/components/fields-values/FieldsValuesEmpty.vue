<script setup lang="ts">
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { tScoped } from "@/modules/common/lib/utils";
import { RiFilterOffLine } from "@remixicon/vue";
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
        <RiFilterOffLine />
      </EmptyMedia>
    </EmptyHeader>
    <EmptyTitle>{{ t("title") }}</EmptyTitle>
    <EmptyDescription>{{ t("description") }}</EmptyDescription>
  </Empty>
</template>
