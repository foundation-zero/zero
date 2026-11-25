import { ENV } from "@env";
import { cacheExchange, Client, fetchExchange } from "@urql/vue";

/**
 * Used directly rather than through `useQuery`: in a Pinia store or outside the alarms app,
 * `useQuery` finds the app-wide Hasura client, which would send its token to the bridge.
 */
const client = new Client({
  url: ENV.VITE_MQTT_GRAPHQL_API_SERVER_URL ?? "/api/mqtt-graphql/graphql",
  exchanges: [cacheExchange, fetchExchange],
  // zero-mqtt-graphql only accepts POST; urql would send short queries as GET.
  preferGetMethod: false,
});

export default client;
