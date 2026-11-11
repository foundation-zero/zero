import { ENV } from "@env";
import { Client, fetchExchange, OperationContext } from "@urql/vue";

// thrs-api: thrsim's simulator controls, the automation mode and the mutations, until they move
// to MQTT GraphQL too.
export const context: Partial<OperationContext> = {
  url: ENV.VITE_THRS_API_SERVER_URL ?? "/api/thrs/graphql",
};

export const client = new Client({
  url: context.url!,
  exchanges: [fetchExchange],
});

// The MQTT GraphQL API (zero-mqtt-graphql), which thrapp's views and thrsim's pages read from.
const mqttGraphqlUrl = ENV.VITE_MQTT_GRAPHQL_API_SERVER_URL ?? "/api/mqtt-graphql/graphql";

export const mqttGraphqlContext: Partial<OperationContext> = { url: mqttGraphqlUrl };

export const mqttGraphqlClient = new Client({
  url: mqttGraphqlUrl,
  exchanges: [fetchExchange],
});
