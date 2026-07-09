<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { tScoped } from "@/modules/common/lib/utils";
import { RiResetLeftLine } from "@remixicon/vue";

const t = tScoped("thrapp.parameters");
</script>

<template>
  <Button>{{ t("actions.resetToDefaults") }}<RiResetLeftLine /></Button>
</template>
