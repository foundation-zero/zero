<script setup lang="ts">
import { LightControl } from "@/@types";
import { LampCeiling, LampWallUp } from "lucide-vue-next";
import { toRefs } from "vue";
import { LightsSlider } from "../lights-slider";
import { List, ListItem, ListRoot } from "../list";
import ListHeader from "../list/ListHeader.vue";
import { ZSpacer } from "../spacer";
import { Switch } from "../switch";

const props = defineProps<{ name: string; lights: LightControl[] }>();
const { lights, name } = toRefs(props);
</script>

<template>
  <ListRoot>
    <ListHeader>{{ name }}</ListHeader>
    <List>
      <ListItem
        v-for="(light, index) in lights"
        :key="light.name"
        class="flex-col space-y-3 py-6"
      >
        <span class="flex w-full items-center">
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
          <span class="text-md font-medium"> {{ light.name }}</span>
          <ZSpacer />
          <Switch v-model:checked="light.on"></Switch>
        </span>

        <LightsSlider
          v-model:brightness="light.brightness"
          :on="light.on"
        />
      </ListItem>
    </List>
  </ListRoot>
</template>
