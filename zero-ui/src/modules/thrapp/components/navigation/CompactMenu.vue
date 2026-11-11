<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { DialogOverlay } from "@/components/ui/dialog";
import { AppLauncher } from "@/modules/common/components/app-launcher";
import { DarkModeToggle } from "@/modules/common/components/dark-mode";
import { tScoped } from "@/modules/common/lib/utils";
import { RiBookOpenLine, RiCloseLine, RiMenuLine } from "@remixicon/vue";
import { useMediaQuery } from "@vueuse/core";
import {
  DialogClose,
  DialogContent,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "reka-ui";
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { ICON_BUTTON_CLASS } from "./navigation.consts";
import { useThrappNavigation } from "./navigation.utils";
import ThrappLogo from "./ThrappLogo.vue";

const t = tScoped("thrapp.components.navigation");

const route = useRoute();
const { tabs, documentation } = useThrappNavigation();

const open = ref(false);

// The menu only exists below the desktop breakpoint; navigating or growing past it closes it.
const isDesktop = useMediaQuery("(min-width: 90rem)");
watch([() => route.fullPath, isDesktop], () => {
  open.value = false;
});
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger as-child>
      <Button
        variant="ghost"
        size="icon"
        :class="ICON_BUTTON_CLASS"
        :aria-label="t('openMenu')"
      >
        <RiMenuLine class="size-5" />
      </Button>
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="bg-black/60 max-md:hidden" />
      <DialogContent
        :aria-describedby="undefined"
        class="bg-background border-border-subtle data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 md:data-[state=open]:slide-in-from-left md:data-[state=closed]:slide-out-to-left fixed inset-0 z-50 flex flex-col duration-200 outline-none md:right-auto md:w-90 md:border-r"
      >
        <DialogTitle class="sr-only">{{ t("menu") }}</DialogTitle>

        <div class="flex h-14 shrink-0 items-center gap-1 px-4">
          <ThrappLogo />
          <span class="grow" />
          <DarkModeToggle :class="ICON_BUTTON_CLASS" />
          <span class="pointer-coarse:[&_[data-slot=button]]:size-11">
            <AppLauncher />
          </span>
          <DialogClose as-child>
            <Button
              variant="ghost"
              size="icon"
              :class="ICON_BUTTON_CLASS"
              :aria-label="t('closeMenu')"
            >
              <RiCloseLine class="size-5" />
            </Button>
          </DialogClose>
        </div>

        <nav
          :aria-label="t('mainNavigation')"
          class="min-h-0 flex-1 overflow-y-auto px-4"
        >
          <ul>
            <li
              v-for="tab in tabs"
              :key="tab.name"
            >
              <RouterLink
                :to="tab.to"
                :aria-current="tab.active ? 'page' : undefined"
                class="focus-visible:ring-brand flex h-13 items-center border-b text-base uppercase transition-colors outline-none focus-visible:ring-2 focus-visible:ring-inset"
                :class="
                  tab.active
                    ? 'border-attention text-foreground'
                    : 'border-border-subtle text-muted-foreground hover:text-foreground'
                "
              >
                {{ t(tab.label) }}
              </RouterLink>
            </li>
          </ul>
        </nav>

        <div class="border-border-subtle shrink-0 border-t px-4">
          <RouterLink
            :to="documentation.to"
            :aria-current="documentation.active ? 'page' : undefined"
            class="focus-visible:ring-brand flex h-14 items-center gap-2 text-sm transition-colors outline-none focus-visible:ring-2 focus-visible:ring-inset"
            :class="
              documentation.active
                ? 'text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            "
          >
            <RiBookOpenLine
              class="size-4"
              :class="{ 'text-attention': documentation.active }"
            />
            {{ t("documentation") }}
          </RouterLink>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
