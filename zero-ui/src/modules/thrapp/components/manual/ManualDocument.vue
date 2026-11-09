<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { onMounted, useTemplateRef, watch } from "vue";
import "./manual.css";
import { paintModes } from "./manual.utils";

const props = defineProps<{ html: string; class?: string }>();

const article = useTemplateRef<HTMLElement>("article");

onMounted(() => paintModes(article.value!));
watch(
  () => props.html,
  () => paintModes(article.value!),
  { flush: "post" },
);
</script>

<template>
  <!-- Manuals are HTML fragments committed to this repository, not user input. -->
  <!-- eslint-disable vue/no-v-html -->
  <article
    ref="article"
    :class="cn('manual', props.class)"
    v-html="html"
  />
</template>
