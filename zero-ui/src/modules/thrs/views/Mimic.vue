<script setup lang="ts">
import Label from "@/components/ui/label/Label.vue";
import { Switch } from "@/components/ui/switch";
import { BoilerLegend, LegendTrigger } from "@/modules/thrapp/components/legends";
import { MimicTooltipProvider } from "@/modules/thrapp/components/tooltip";
import NoopTooltipProvider from "@/modules/thrapp/components/tooltip/NoopTooltipProvider.vue";
import DhwModule from "@/modules/thrapp/mimics/modules/dhw/DhwModule.vue";
import { DHW_MIMIC_DATA } from "@/modules/thrapp/mimics/modules/dhw/data";
import { GraphQLProvider, MockProvider } from "@/modules/thrapp/mimics/providers";
import { DEFINITIONS } from "@/modules/thrs/lib/consts";
import { computed, inject, Ref, ref } from "vue";
import { useI18n } from "vue-i18n";

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;

const demoMode = ref(false);
const provider = computed(() => (demoMode.value ? MockProvider : GraphQLProvider));

const { t } = useI18n();
</script>
<template>
  <component :is="provider">
    <section
      class="flex h-full justify-around gap-x-4 max-lg:flex-col-reverse portrait:flex-col-reverse"
    >
      <aside
        class="flex w-full flex-row-reverse items-center justify-between landscape:lg:w-62.5 landscape:lg:flex-col landscape:lg:items-start"
      >
        <div class="flex items-center gap-3">
          <Switch v-model="demoMode" />
          <Label>{{ t("thrapp.labels.demoMode") }}</Label>
        </div>

        <LegendTrigger>
          <NoopTooltipProvider>
            <BoilerLegend v-if="currentDefinition === 'dhw'" />
          </NoopTooltipProvider>
        </LegendTrigger>
      </aside>

      <MimicTooltipProvider :source="DHW_MIMIC_DATA">
        <DhwModule
          v-if="currentDefinition === 'dhw'"
          class="mx-auto my-auto max-h-[calc(100svh-14em)]"
        />
      </MimicTooltipProvider>
    </section>
  </component>
</template>
