<script setup lang="ts">
import ControlModule from "@/components/modules/thrs/ControlModule.vue";
import thrsSchema from "@/graphql/thrs/schema.graphql?raw";
import { Client, fetchExchange, provideClient } from "@urql/vue";
import { buildASTSchema, GraphQLField, GraphQLNonNull, GraphQLObjectType, parse } from "graphql";

const ast = parse(thrsSchema);
const schema = buildASTSchema(ast);
const query = schema.getQueryType();
const moduleNode = query?.getFields()?.modules;

const client = new Client({
  url: "/api/thrs/graphql",
  exchanges: [fetchExchange],
});
provideClient(client);

const modules =
  (
    (moduleNode as GraphQLField<unknown, unknown, unknown> | undefined)?.type as
      | GraphQLNonNull<GraphQLObjectType>
      | undefined
  )?.ofType?.getFields() ?? {};
</script>
<template>
  <ControlModule
    v-for="(module, key) in modules"
    :key="key"
    :module="key as string"
    :schema="module"
    :client="client"
  />
</template>
