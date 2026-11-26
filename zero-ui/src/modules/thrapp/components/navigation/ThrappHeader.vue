<script setup lang="ts">
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLauncher } from "@/modules/common/components/app-launcher";
import { DarkModeToggle } from "@/modules/common/components/dark-mode";
import { TopNavToolbar } from "@/modules/common/components/navigation";
import TopNavZero from "@/modules/common/components/navigation/TopNavZero.vue";
import { tScoped } from "@/modules/common/lib/utils";
import CompactMenu from "./CompactMenu.vue";
import DocumentationButton from "./DocumentationButton.vue";
import { BANNER_BUTTON_CLASS, ICON_BUTTON_CLASS } from "./navigation.consts";
import MainNav from "./MainNav.vue";
import ThrappLogo from "./ThrappLogo.vue";

const t = tScoped("thrapp.components.navigation");
</script>

<template>
  <TooltipProvider>
    <header class="bg-background relative z-20 shrink-0">
      <div class="max-desktop:hidden">
        <TopNavToolbar class="thrapp-banner dark text-foreground h-14 border-0 px-6 md:px-6">
          <template #center>
            <TopNavZero />
          </template>
          <template #right-content>
            <div class="flex items-center gap-4">
              <DarkModeToggle :class="[ICON_BUTTON_CLASS, BANNER_BUTTON_CLASS]" />
              <span
                class="[&_[data-slot=button]]:bg-background/50 [&_[data-slot=button]]:text-brand [&_[data-slot=button]]:rounded-md pointer-coarse:[&_[data-slot=button]]:size-11"
              >
                <AppLauncher />
              </span>
            </div>
          </template>
        </TopNavToolbar>

        <nav
          :aria-label="t('mainNavigation')"
          class="border-border-subtle font-ui flex h-[73px] items-center gap-6 border-b px-6"
        >
          <ThrappLogo class="mr-4" />
          <MainNav />
          <span class="grow" />
          <div class="flex items-center gap-6">
            <DocumentationButton />
          </div>
        </nav>
      </div>

      <div
        class="thrapp-banner dark text-foreground desktop:hidden flex h-14 items-center gap-2 px-2 md:px-4"
      >
        <CompactMenu />
        <ThrappLogo />
      </div>

      <slot />
    </header>
  </TooltipProvider>
</template>

<style scoped>
/*
 * The banner stays dark in both themes (its `dark` class scopes the dark tokens to it), with a
 * fixed-size ellipse centred above the bar so it does not stretch with the viewport (design spec).
 */
.thrapp-banner {
  background:
    radial-gradient(
      1334px 237px at 50% -63px,
      color-mix(in srgb, var(--color-brand-a-400) 50%, transparent),
      transparent
    ),
    var(--background);
}
</style>
