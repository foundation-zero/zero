<script setup lang="ts">
import LightGroup from "@/components/LightGroup.vue";
</script>

<template>
  <section class="grid container grid-cols-1 lg:grid-cols-2 gap-10 max-sm:pb-[96px] md:pb-[32px]">
    <LightGroup
      class="columns-1"
      name="Bathroom"
      :lights="['Main light', 'Ambient']"
    />
    <LightGroup
      class="columns-1"
      name="Cabin"
      :lights="['Main light', 'Ambient']"
    />
    <LightGroup
      class="columns-1"
      name="Sauna"
      :lights="['Main light', 'Ambient']"
    />
  </section>
</template>
