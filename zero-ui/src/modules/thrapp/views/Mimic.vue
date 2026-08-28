<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue";
import { Switch } from "@/components/ui/switch";
import { LegendTrigger } from "@/modules/thrapp/components/legends";
import { MimicTooltipProvider } from "@/modules/thrapp/components/tooltip";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import GridPattern from "@/modules/thrapp/mimics/modules/GridPattern.vue";
import { GraphQLProvider, MockProvider } from "@/modules/thrapp/mimics/providers";
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { MIMICS } from "../router/mimics";

const demoMode = ref(false);
const provider = computed(() => (demoMode.value ? MockProvider : GraphQLProvider));

const { currentRoute } = useRouter();
const { t } = useI18n();

const currentMimic = computed(() => MIMICS[currentRoute.value.params.module as keyof ThrsModules]);
</script>
<template>
  <component :is="provider">
    <section
      class="relative flex h-full justify-around gap-x-4 max-lg:flex-col-reverse portrait:flex-col-reverse"
    >
      <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" />
      <aside
        class="z-1 flex w-full flex-row-reverse items-center justify-between landscape:lg:w-62.5 landscape:lg:flex-col landscape:lg:items-start"
      >
        <div class="flex items-center gap-3">
          <Switch v-model="demoMode" />
          <Label>{{ t("thrapp.labels.demoMode") }}</Label>
        </div>

        <LegendTrigger>
          <NoopTooltipProvider>
            <component
              :is="currentMimic?.legend"
              v-if="currentMimic?.legend"
            />
          </NoopTooltipProvider>
        </LegendTrigger>
      </aside>

      <MimicTooltipProvider
        v-if="currentMimic"
        :source="currentMimic.data"
      >
        <component
          :is="currentMimic.component"
          class="z-1 mx-auto my-auto max-h-[calc(100svh-14em)]"
        />
      </MimicTooltipProvider>
    </section>
  </component>
</template>
