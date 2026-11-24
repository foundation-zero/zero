<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { onMounted, useTemplateRef, watch } from "vue";
import "./manual.css";
import "./manual-app.css";
import { decorateManual } from "./manual.utils";

const props = defineProps<{
  html: string;
  /** Lay the manual out on A4, as the crew PDF and the print view show it. */
  printed?: boolean;
  class?: string;
}>();
const emit = defineEmits<{ rendered: [] }>();

const article = useTemplateRef<HTMLElement>("article");

const decorate = async () => {
  await decorateManual(article.value!, { fitDiagrams: props.printed });
  emit("rendered");
};

onMounted(decorate);
watch(() => props.html, decorate, { flush: "post" });
</script>

<template>
  <!-- Manuals are HTML fragments committed to this repository, not user input. -->
  <!-- eslint-disable vue/no-v-html -->
  <article
    ref="article"
    :class="cn('manual manual-app', printed && 'printed', props.class)"
    v-html="html"
  />
</template>
