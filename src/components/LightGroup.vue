<script setup lang="ts">
import { LightControl } from "@/@types";
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { toRefs } from "vue";
import { CardContent, CardHeader, CardTitle } from "./ui/card";
import List from "./ui/list/List.vue";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";

const props = defineProps<{ name: string; lights: LightControl[] }>();
const { lights, name } = toRefs(props);
</script>

<template>
  <article class="grid">
    <header class="text-xs uppercase">{{ name }}</header>
    <List class="border">
      <li
        v-for="(light, index) in lights"
        :key="light.name"
      >
        <CardHeader>
          <CardTitle class="flex items-center justify-between">
            <span class="text-md">
              <LampCeiling
                v-if="index == 0"
                class="mr-3 inline"
                :size="18"
              />
              <LampWallUp
                v-if="index == 1"
                class="mr-3 inline"
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
      </li>
    </List>
  </article>
</template>
