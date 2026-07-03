<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { RiApps2Line } from "@remixicon/vue";
import { useI18n } from "vue-i18n";
import { ZeroLogo } from "../zero-logo";

const { t } = useI18n();

type App = {
  name: string;
  link: string;
};

const APPS: App[] = [
  {
    name: "loads",
    link: "/loads",
  },
  {
    name: "thrs",
    link: "/thrs",
  },
  {
    name: "thrapp",
    link: "/thrapp",
  },
  {
    name: "domestic",
    link: "/domestic",
  },
  {
    name: "grafana",
    link: "/grafana",
  },
];
</script>
<template>
  <Popover>
    <PopoverTrigger>
      <Button
        variant="ghost"
        size="icon"
      >
        <RiApps2Line class="size-5" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="border-0 p-0">
      <ul class="grid">
        <RouterLink
          v-for="app in APPS"
          :key="app.name"
          :to="app.link"
        >
          <li
            class="hover:bg-background hover:text-foreground flex flex-nowrap items-center px-4 py-3 text-nowrap"
          >
            <ZeroLogo />
            <span class="text-sm font-light uppercase">- {{ t(`apps.${app.name}`) }}</span>
          </li>
        </RouterLink>
      </ul>
    </PopoverContent>
  </Popover>
</template>
