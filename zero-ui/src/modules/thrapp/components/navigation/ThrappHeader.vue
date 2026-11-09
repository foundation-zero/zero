<script setup lang="ts">
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppLauncher } from "@/modules/common/components/app-launcher";
import { DarkModeToggle } from "@/modules/common/components/dark-mode";
import { TopNavToolbar } from "@/modules/common/components/navigation";
import TopNavZero from "@/modules/common/components/navigation/TopNavZero.vue";
import { tScoped } from "@/modules/common/lib/utils";
import CompactMenu from "./CompactMenu.vue";
import DocumentationButton from "./DocumentationButton.vue";
import { ICON_BUTTON_CLASS } from "./navigation.consts";
import MainNav from "./MainNav.vue";
import ThrappLogo from "./ThrappLogo.vue";

const t = tScoped("thrapp.components.navigation");
</script>

<template>
  <TooltipProvider>
    <header class="bg-background relative z-20 shrink-0">
      <div class="max-desktop:hidden">
        <TopNavToolbar class="thrapp-banner h-14 border-0 px-6 md:px-6">
          <template #center>
            <TopNavZero />
          </template>
          <template #right-content>
            <div class="flex items-center gap-1">
              <DarkModeToggle :class="ICON_BUTTON_CLASS" />
              <span class="pointer-coarse:[&_[data-slot=button]]:size-11">
                <AppLauncher />
              </span>
            </div>
          </template>
        </TopNavToolbar>

        <nav
          :aria-label="t('mainNavigation')"
          class="border-border-subtle flex h-[73px] items-center gap-6 border-b px-6"
        >
          <ThrappLogo class="mr-4" />
          <MainNav />
          <span class="grow" />
          <div class="flex items-center gap-6">
            <DocumentationButton />
          </div>
        </nav>
      </div>

      <div class="thrapp-banner desktop:hidden flex h-14 items-center gap-2 px-2 md:px-4">
        <CompactMenu />
        <ThrappLogo />
      </div>

      <slot />
    </header>
  </TooltipProvider>
</template>

<style lang="scss" scoped>
// Same gradient as the shared TopNav banner (provided by the design team).
:global(.dark .thrapp-banner) {
  background:
    radial-gradient(
      43.74% 35.44% at 50.03% 36.53%,
      var(----general---brand-dull, rgba(86, 133, 169, 0.2)) 0%,
      rgba(153, 182, 204, 0) 100%
    ),
    var(----general---background-muted, #121619);
}
</style>
