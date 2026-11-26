<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { cn, tScoped } from "@/modules/common/lib/utils";
import { RiBookOpenLine } from "@remixicon/vue";
import { ICON_BUTTON_CLASS } from "./navigation.consts";
import { useThrappNavigation } from "./navigation.utils";

const t = tScoped("thrapp.components.navigation");

const { documentation } = useThrappNavigation();
</script>

<template>
  <Tooltip>
    <TooltipTrigger as-child>
      <Button
        as-child
        variant="ghost"
        size="icon"
        :class="
          cn(
            ICON_BUTTON_CLASS,
            'focus-visible:ring-brand hover:bg-foreground/5 relative rounded-xs focus-visible:ring-2',
            documentation.active &&
              'bg-foreground/5 text-foreground after:bg-attention after:absolute after:inset-x-0 after:bottom-0 after:mx-auto after:h-0.5 after:w-5 after:rounded-[1px]',
          )
        "
      >
        <RouterLink
          :to="documentation.to"
          :aria-current="documentation.active ? 'page' : undefined"
          :aria-label="t('documentation')"
          data-testid="documentation-button"
        >
          <RiBookOpenLine class="size-5" />
        </RouterLink>
      </Button>
    </TooltipTrigger>
    <TooltipContent>{{ t("documentation") }}</TooltipContent>
  </Tooltip>
</template>
