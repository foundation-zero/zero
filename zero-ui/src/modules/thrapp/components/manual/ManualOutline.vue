<script setup lang="ts">
import { cn, tScoped } from "@common/lib/utils";
import { ManualSection } from "./manual.types";

const props = defineProps<{ sections: Array<ManualSection>; active?: string; class?: string }>();

const t = tScoped("thrapp.views.documentation");
</script>

<template>
  <nav
    :aria-label="t('outline')"
    :class="
      cn('bg-background border-border flex flex-col gap-3.5 rounded-lg border p-5', props.class)
    "
  >
    <p class="text-muted-foreground text-xs/3 uppercase">
      {{ t("outline") }}
    </p>
    <a
      v-for="section in sections"
      :key="section.id"
      :href="`#${section.id}`"
      :aria-current="section.id === active ? 'location' : undefined"
      :class="
        cn(
          'text-muted-foreground hover:text-foreground text-sm/3.5 font-medium transition-colors',
          section.id === active && 'text-foreground',
        )
      "
    >
      {{ section.title }}
    </a>
  </nav>
</template>
