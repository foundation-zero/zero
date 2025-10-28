<script setup lang="ts">
import NavPills from "@/components/modules/hmi/NavPills.vue";
import Toolbar from "@/components/modules/thrs/Toolbar.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/components/modules/hmi/SimulationActions.vue";
import thrsSchema from "@/graphql/thrs/schema.graphql?raw";
import { buildASTSchema, GraphQLField, GraphQLNonNull, GraphQLObjectType, parse } from "graphql";

import { client } from "@/graphql/thrs/client";
import { provideClient } from "@urql/vue";
import { computed, provide, ref } from "vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();
const ast = parse(thrsSchema);
const schema = buildASTSchema(ast);
const query = schema.getQueryType();
const moduleNode = query?.getFields()?.modules;

const modules =
  (
    (moduleNode as GraphQLField<unknown, unknown, unknown> | undefined)?.type as
      | GraphQLNonNull<GraphQLObjectType>
      | undefined
  )?.ofType?.getFields() ?? {};

const currentModuleKey = ref(Object.keys(modules)[0]);
const currentModule = computed(() => modules[currentModuleKey.value]);

provide("currentModule", currentModule);
</script>

<template>
  <main class="h-svh pt-[96px]">
    <Suspense>
      <slot />
    </Suspense>
  </main>
  <nav class="fixed top-0 right-0 left-0 backdrop-blur-md">
    <Toolbar class="items-center px-4 py-1">
      <template #left>
        <div class="flex items-end">
          <h4 class="text-4xl font-semibold uppercase">{{ t("labels.hmi") }}</h4>
          <NavPills
            v-model:active-module="currentModuleKey"
            class="ml-12"
            :modules="modules"
          />
        </div>
      </template>

      <template #right>
        <SimulationActions />
      </template>
    </Toolbar>
  </nav>
</template>
