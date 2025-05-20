<script setup lang="ts">
import { Collapsible } from "@/components/ui/collapsible";
import { NavList, NavListItem } from "@/components/ui/nav-list";
import {
  BatteryCharging,
  Droplet,
  Droplets,
  Fan,
  LampCeiling,
  ThermometerSnowflake,
} from "lucide-vue-next";
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <Collapsible
    :title="$t('labels.environment')"
    :open="true"
  >
    <NavList>
      <NavListItem
        :to="{ name: 'env:temperature' }"
        :active="route.name === 'env:temperature'"
      >
        <ThermometerSnowflake
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.temperature") }}
        </span>
      </NavListItem>
      <NavListItem
        :to="{ name: 'env:humidity' }"
        :active="route.name === 'env:humidity'"
      >
        <Droplets
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.humidity") }}
        </span>
      </NavListItem>
      <NavListItem
        :to="{ name: 'env:ventilation' }"
        :active="route.name === 'env:ventilation'"
      >
        <Fan
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.ventilation") }}
        </span>
      </NavListItem>
      <NavListItem
        :to="{ name: 'env:lights' }"
        :active="route.name === 'env:lights'"
      >
        <LampCeiling
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.lights") }}
        </span>
      </NavListItem>
    </NavList>
  </Collapsible>
  <Collapsible
    :title="$t('labels.utilities')"
    :open="true"
  >
    <NavList>
      <NavListItem
        :to="{ name: 'env:temperature' }"
        disabled
      >
        <Droplet
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.water") }}
        </span>
      </NavListItem>
      <NavListItem
        :to="{ name: 'env:temperature' }"
        disabled
      >
        <BatteryCharging
          :size="16"
          stroke-width="2"
        />
        <span class="ml-2.5">
          {{ $t("labels.power") }}
        </span>
      </NavListItem>
    </NavList>
  </Collapsible>
</template>
