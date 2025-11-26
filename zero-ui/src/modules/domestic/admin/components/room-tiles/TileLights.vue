<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { Room, ValidationStatus } from "@/modules/domestic/types";
import { ValueTile } from "@common/components/value-tile";
import { Lightbulb, LightbulbOff } from "lucide-vue-next";
import { computed } from "vue";
import { useToggleableLights } from ".";

const props = defineProps<{ room: Room }>();

const { controls, someLightsAreOn, toggle } = useToggleableLights(computed(() => [props.room]));
</script>

<template>
  <ValueTile
    v-if="controls.length > 0"
    :title="room.name"
    :class="{ on: someLightsAreOn }"
    selectable
    :state="ValidationStatus.UNKNOWN"
    @click="toggle"
  >
    <template #center>
      <Switch
        :checked="someLightsAreOn"
        class="mb-1 scale-125 md:scale-200"
      />
    </template>
    <template #bottom-right>
      <Lightbulb
        v-if="someLightsAreOn"
        class="mb-1 h-[1.5em] w-[1.5em]"
        stroke-width="2.5"
      />
      <LightbulbOff
        v-else
        class="mb-1 h-[1.5em] w-[1.5em]"
        stroke-width="1"
      />
    </template>
  </ValueTile>
</template>
