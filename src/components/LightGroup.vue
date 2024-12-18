<script setup lang="ts">
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { Card, CardTitle, CardHeader, CardContent } from "./ui/card";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";
import { LightControl } from "@/@types";
import { toRefs } from "vue";

const props = defineProps<{ name: string; lights: LightControl[] }>();
const { lights, name } = toRefs(props);
</script>

<template>
  <article class="grid gap-3">
    <header class="text-xs uppercase">{{ name }}</header>
    <Card
      class="shadow-none"
      v-for="(light, index) in lights"
      :key="light.name"
    >
      <CardHeader>
        <CardTitle class="flex justify-between items-center">
          <span class="text-md">
            <LampCeiling
              v-if="index == 0"
              class="inline mr-3"
              :size="18"
            />
            <LampWallUp
              v-if="index == 1"
              class="inline mr-3"
              :size="18"
            />
            {{ light.name }}</span
          >
          <Switch v-model:checked="light.on"></Switch>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Slider
          :disabled="!light.on"
          :min="0"
          :max="100"
          :model-value="[light.on ? light.brightness : 0]"
          :class="{ 'opacity-50': !light.on }"
          @update:model-value="(val) => (light.brightness = val?.[0] ?? 0)"
        />
      </CardContent>
    </Card>
  </article>
</template>
