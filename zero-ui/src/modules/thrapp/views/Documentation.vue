<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Empty, EmptyHeader, EmptyTitle } from "@/components/ui/empty";
import { tScoped } from "@/modules/common/lib/utils";
import {
  linkParameters,
  ManualDocument,
  ManualOutline,
  ManualSection,
  outlineManual,
  readManualStamp,
} from "@/modules/thrapp/components/manual";
import { RiPrinterLine } from "@remixicon/vue";
import { computedAsync } from "@vueuse/core";
import { computed, ref, useTemplateRef } from "vue";
import { useRoute, useRouter } from "vue-router";
import { DOCUMENTATION } from "../router/documentation";
import { MimicKey } from "../router/mimics";
import { PARAMETERS } from "../router/parameters";

// How far below the top of the page a section heading counts as the one being read.
const READING_LINE = 96;

const t = tScoped("thrapp.views.documentation");

const route = useRoute();
const router = useRouter();
const module = computed(() => route.params.module as MimicKey);

// A parameter's link opens the Controls page with that parameter selected.
const controlsHref = (field: string) =>
  router.resolve({
    name: "thrs/control",
    params: { module: module.value },
    query: { parameter: field },
  }).href;
const loadManual = computed(() => DOCUMENTATION[module.value]);
const html = computedAsync(async () => loadManual.value?.());
const stamp = computed(() => html.value && readManualStamp(html.value));
const issued = computed(
  () =>
    stamp.value &&
    new Intl.DateTimeFormat("en-GB", { dateStyle: "long", timeZone: "UTC" }).format(
      new Date(stamp.value.issued),
    ),
);

const page = useTemplateRef<HTMLElement>("page");
const sections = ref<Array<ManualSection>>([]);
const active = ref<string>();

const onRendered = () => {
  const article = page.value!.querySelector<HTMLElement>("article.manual")!;
  sections.value = outlineManual(article);
  if (module.value in PARAMETERS) linkParameters(article, controlsHref);
  followReading();
};

const followReading = () => {
  const { scrollTop, clientHeight, scrollHeight } = page.value!;
  const readingLine = page.value!.getBoundingClientRect().top + READING_LINE;
  const atBottom = scrollTop + clientHeight >= scrollHeight - 2;
  const read = sections.value.filter(
    ({ id }) => document.getElementById(id)!.getBoundingClientRect().top <= readingLine,
  );
  active.value = (atBottom ? sections.value : read).slice(-1)[0]?.id ?? sections.value[0]?.id;
};

// The outline's links scroll the page rather than the router, which would treat the
// hash as a navigation. The manual's parameter links go through the router, so the
// app stays loaded; a modified click still opens them as the browser would.
const followLink = (event: MouseEvent) => {
  const target = event.target as Element;
  const section = target.closest<HTMLAnchorElement>('a[href^="#"]');
  const heading = section && document.getElementById(decodeURIComponent(section.hash.slice(1)));
  if (heading) {
    event.preventDefault();
    heading.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }

  const parameter = target.closest<HTMLAnchorElement>("article.manual a[href]");
  const plainClick = !(event.metaKey || event.ctrlKey || event.shiftKey || event.altKey);
  if (!parameter || !plainClick || event.button !== 0) return;
  event.preventDefault();
  router.push(parameter.getAttribute("href")!);
};
</script>

<template>
  <section
    ref="page"
    class="-mx-4 min-h-0 grow overflow-y-auto px-4 pb-8 md:-mx-6 md:px-6"
    @scroll.passive="followReading"
    @click="followLink"
  >
    <div
      v-if="loadManual"
      class="flex items-start gap-6"
    >
      <ManualOutline
        :sections="sections"
        :active="active"
        class="sticky top-0 hidden w-78 shrink-0 xl:flex"
      />
      <div
        class="bg-background border-border-subtle max-w-300 min-w-0 flex-1 rounded-lg border px-5 py-6 md:px-12 md:py-10"
      >
        <header
          class="border-border-subtle text-muted-foreground mb-8 flex flex-wrap items-center justify-between gap-x-6 gap-y-3 border-b pb-4 text-sm"
        >
          <dl
            v-if="stamp"
            class="flex flex-wrap gap-x-6 gap-y-1"
          >
            <div class="flex gap-1.5">
              <dt>{{ t("version") }}</dt>
              <dd class="text-foreground font-mono">{{ stamp.version }}</dd>
            </div>
            <div class="flex gap-1.5">
              <dt>{{ t("issued") }}</dt>
              <dd class="text-foreground">
                <time :datetime="stamp.issued">{{ issued }}</time>
              </dd>
            </div>
          </dl>
          <Button
            as-child
            variant="secondary"
            size="sm"
            class="ml-auto"
          >
            <RouterLink
              :to="{ name: 'thrs/documentation/print', params: { module: route.params.module } }"
              target="_blank"
            >
              <RiPrinterLine />
              {{ t("viewPrinted") }}
            </RouterLink>
          </Button>
        </header>
        <ManualDocument
          v-if="html"
          :html="html"
          @rendered="onRendered"
        />
      </div>
    </div>
    <Empty v-else>
      <EmptyHeader>
        <EmptyTitle>{{ t("empty") }}</EmptyTitle>
      </EmptyHeader>
    </Empty>
  </section>
</template>
