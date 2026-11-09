<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
} from "@/components/ui/select";
import { tScoped } from "@/modules/common/lib/utils";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { RiArrowDropDownLine, RiArrowRightLine } from "@remixicon/vue";
import { SelectIcon, SelectTrigger } from "reka-ui";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { getModuleOptionGroups, getParentModule } from "./sub-navigation.utils";

const props = defineProps<{ modules: MimicKey[]; activeModule?: MimicKey }>();

const { t } = useI18n();
const tNav = tScoped("thrapp.components.subNavigation");
const moduleName = (module: MimicKey) => t(`thrapp.modules.${module}`);

const route = useRoute();
const router = useRouter();

const groups = computed(() => {
  const views = (route.meta.views as Partial<Record<MimicKey, unknown>>) ?? {};
  return getModuleOptionGroups((module) => props.modules.includes(module) && !!views[module]);
});

const parentModule = computed(() => props.activeModule && getParentModule(props.activeModule));

const select = async (module: unknown) => {
  if (module && module !== props.activeModule) {
    await router.push({ name: route.name as string, params: { module: module as MimicKey } });
  }
};
</script>

<template>
  <Select
    :model-value="activeModule"
    @update:model-value="select"
  >
    <SelectTrigger
      class="focus-visible:ring-brand flex h-9 min-w-0 cursor-pointer items-center gap-2 rounded-sm text-base leading-4 font-medium outline-none focus-visible:ring-2"
      data-testid="module-selector"
    >
      <span class="text-muted-foreground shrink-0">
        {{ parentModule ? moduleName(parentModule) : tNav("module") }}
      </span>
      <RiArrowRightLine class="text-muted-foreground size-3 shrink-0" />
      <span class="text-foreground truncate">{{ activeModule && moduleName(activeModule) }}</span>
      <SelectIcon as-child>
        <RiArrowDropDownLine class="size-5 shrink-0" />
      </SelectIcon>
    </SelectTrigger>

    <SelectContent
      align="start"
      class="w-[270px] rounded-lg border-0"
    >
      <SelectGroup
        v-for="group in groups"
        :key="group.key"
        class="border-inverse-border-subtle not-first:border-t"
      >
        <SelectLabel
          class="text-inverse-muted-foreground/70 px-4 pt-4 pb-1 text-[11px] font-semibold tracking-[0.1em] uppercase"
        >
          {{ tNav(`groups.${group.key}`) }}
        </SelectLabel>
        <template
          v-for="module in group.modules"
          :key="module.key"
        >
          <SelectItem
            :value="module.key"
            :disabled="module.disabled"
            class="h-10 pr-8 pl-8"
          >
            {{ moduleName(module.key) }}
          </SelectItem>
          <SelectItem
            v-for="subModule in module.subModules"
            :key="subModule"
            :value="subModule"
            class="py-1.5 pr-8 pl-12 text-xs font-normal"
          >
            {{ moduleName(subModule) }}
          </SelectItem>
        </template>
      </SelectGroup>
    </SelectContent>
  </Select>
</template>
