<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { ModeBadges, ModeBadgeSize } from "@/modules/thrapp/mimics/components/mode-badge";
import { HTMLAttributes } from "vue";

const props = defineProps<{ module?: keyof ThrsModules; class?: HTMLAttributes["class"] }>();

const t = tScoped("thrapp.components.subNavigation");
</script>

<template>
  <div :class="cn('flex items-center gap-3', props.class)">
    <div class="bg-border-subtle hidden h-5 w-px shrink-0 lg:block" />
    <span class="text-muted-foreground shrink-0 text-xs leading-5">{{ t("mode") }}</span>
    <div class="flex min-w-0 flex-wrap items-center gap-2">
      <ModeBadges
        :module="module"
        :size="ModeBadgeSize.Navigation"
      />
    </div>
  </div>
</template>
