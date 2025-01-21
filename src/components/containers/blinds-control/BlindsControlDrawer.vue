<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import BlindsList from "./BlindsList.vue";

const open = defineModel<boolean>("open");
defineProps<{ group: BlindsGroup }>();
</script>

<template>
  <Drawer v-model:open="open">
    <DrawerContent>
      <div class="flex flex-col">
        <DrawerHeader class="">
          <div class="mx-auto w-full max-w-sm text-center">
            <DrawerTitle>{{ group.name }}</DrawerTitle>
            <DrawerDescription class="mt-1"> Control the blinds and sheers </DrawerDescription>
          </div>
        </DrawerHeader>

        <BlindsList
          :group="group"
          class="mx-3 mb-3"
        />
      </div>
    </DrawerContent>
  </Drawer>
</template>
