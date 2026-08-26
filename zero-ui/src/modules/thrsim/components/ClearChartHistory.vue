<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { tScoped } from "@/modules/common/lib/utils";
import { RiDeleteBinLine } from "@remixicon/vue";
import { ref } from "vue";
import { useThrsHistory } from "../stores/history";

const $t = tScoped("thrs.components.clearChartHistory");

const isOpen = ref(false);

const { clear } = useThrsHistory();
const clearCache = () => {
  clear();
  isOpen.value = false;
};
</script>

<template>
  <Popover v-model:open="isOpen">
    <PopoverTrigger>
      <Button
        variant="ghost"
        size="icon"
      >
        <RiDeleteBinLine />
      </Button>
    </PopoverTrigger>
    <PopoverContent>
      <header class="mb-3 text-lg font-semibold">{{ $t("title") }}</header>
      <p class="mb-4">{{ $t("description") }}</p>
      <div class="flex justify-end gap-2">
        <Button
          variant="outline"
          @click="isOpen = false"
          >{{ $t("cancelButton") }}</Button
        >
        <Button
          variant="default"
          @click="clearCache"
          >{{ $t("confirmButton") }}</Button
        >
      </div>
    </PopoverContent>
  </Popover>
</template>
