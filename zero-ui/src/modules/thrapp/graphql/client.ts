import { ENV } from "@env";
import { Client, fetchExchange, OperationContext } from "@urql/vue";

// The MQTT GraphQL API (zero-mqtt-graphql), which thrapp and thrsim read from and write to.
const mqttGraphqlUrl = ENV.VITE_MQTT_GRAPHQL_API_SERVER_URL ?? "/api/mqtt-graphql/graphql";

export const mqttGraphqlContext: Partial<OperationContext> = { url: mqttGraphqlUrl };

export const mqttGraphqlClient = new Client({
  url: mqttGraphqlUrl,
  exchanges: [fetchExchange],
});
