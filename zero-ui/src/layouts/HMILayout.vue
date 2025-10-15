<script setup lang="ts">
import NavPills from "@/components/modules/hmi/NavPills.vue";
import Toolbar from "@/components/modules/thrs/Toolbar.vue";
import { useI18n } from "vue-i18n";

import thrsSchema from "@/graphql/thrs/schema.graphql?raw";
import { buildASTSchema, GraphQLField, GraphQLNonNull, GraphQLObjectType, parse } from "graphql";
import { computed, provide, ref } from "vue";

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

      <template #right> </template>
    </Toolbar>
  </nav>
</template>
