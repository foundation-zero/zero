import { ENV } from "@env";
import { cacheExchange, Client, fetchExchange, OperationContext } from "@urql/vue";

export const ALARMS_CONTEXT: Pick<OperationContext, "url"> = {
  url: ENV.VITE_MQTT_GRAPHQL_API_SERVER_URL,
};

const client = new Client({
  url: ALARMS_CONTEXT.url,
  exchanges: [cacheExchange, fetchExchange],
});

export default client;
