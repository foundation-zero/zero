<script setup lang="ts">
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { Card, CardTitle, CardHeader, CardContent } from "./ui/card";
import { Slider } from "./ui/slider";
import { Switch } from "./ui/switch";

defineProps<{ name: string; lights: string[] }>();
</script>

<template>
  <article class="grid gap-3">
    <header class="text-xs uppercase">{{ name }}</header>
    <Card
      v-for="(light, index) in lights"
      :key="light"
    >
      <CardHeader>
        <CardTitle class="flex justify-between items-center">
          <span class="text-lg">
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
            {{ light }}</span
          >
          <Switch></Switch>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Slider
          :min="0"
          :max="100"
          :default-value="[65]"
          :model-value="[65]"
        />
      </CardContent>
    </Card>
  </article>
</template>
