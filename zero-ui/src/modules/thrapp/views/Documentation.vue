<script setup lang="ts">
import { Empty, EmptyHeader, EmptyTitle } from "@/components/ui/empty";
import { tScoped } from "@/modules/common/lib/utils";
import { ManualDocument } from "@/modules/thrapp/components/manual";
import { computedAsync } from "@vueuse/core";
import { computed } from "vue";
import { useRoute } from "vue-router";
import { DOCUMENTATION } from "../router/documentation";
import { MimicKey } from "../router/mimics";

const t = tScoped("thrapp.views.documentation");

const route = useRoute();
const loadManual = computed(() => DOCUMENTATION[route.params.module as MimicKey]);
const html = computedAsync(async () => loadManual.value?.());
</script>

<template>
  <section class="-mx-4 min-h-0 grow overflow-y-auto px-4 pb-8 md:-mx-6 md:px-6">
    <ManualDocument
      v-if="loadManual && html"
      :html="html"
      class="md:px-8 xl:px-16"
    />
    <Empty v-else-if="!loadManual">
      <EmptyHeader>
        <EmptyTitle>{{ t("empty") }}</EmptyTitle>
      </EmptyHeader>
    </Empty>
  </section>
</template>
