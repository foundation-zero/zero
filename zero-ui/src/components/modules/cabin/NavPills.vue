<script setup lang="ts">
import { isBlindsControl, isLightControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { Tabs, TabsList, TabsTrigger } from "@components/shadcn/tabs";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
const { name } = toRefs(useRoute());
const { t } = useI18n();

const { currentRoom } = toRefs(useRoomStore());
const { showSideNav, breakpoints } = toRefs(useUIStore());
const lights = computed(() => currentRoom.value.roomsControls.filter(isLightControl));
const blinds = computed(() => currentRoom.value.roomsControls.filter(isBlindsControl));
</script>

<template>
  <Tabs
    :model-value="String(name)"
    :class="{ 'max-lg:opacity-0': showSideNav && breakpoints.touch }"
  >
    <TabsList
      class="bg-black !bg-opacity-5 backdrop-blur-md dark:bg-white"
      as="nav"
    >
      <RouterLink :to="{ name: 'cabin:airconditioning' }">
        <TabsTrigger value="cabin:airconditioning">
          {{ t("labels.airconditioning.long") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink
        v-if="lights?.length"
        :to="{ name: 'cabin:lights' }"
      >
        <TabsTrigger value="cabin:lights">
          {{ t("labels.lights") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink
        v-if="blinds?.length"
        :to="{ name: 'cabin:blinds' }"
      >
        <TabsTrigger value="cabin:blinds">
          {{ t("labels.blinds") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
