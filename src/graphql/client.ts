import { authExchange } from "@urql/exchange-auth";
import { cacheExchange, Client, fetchExchange, subscriptionExchange } from "@urql/vue";

import { createClient as createWSClient } from "graphql-ws";

const wsClient = createWSClient({
  url: `${import.meta.env.VITE_GRAPHQL_WS_URL}`,

  connectionParams: () => ({
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token") ?? import.meta.env.VITE_GRAPHQL_TOKEN}`,
    },
  }),
});

const client = new Client({
  url: `${import.meta.env.VITE_GRAPHQL_URL}`,
  exchanges: [
    cacheExchange,
    authExchange(async (utils) => {
      const token = localStorage.getItem("token") ?? import.meta.env.VITE_GRAPHQL_TOKEN;

      return {
        addAuthToOperation(operation) {
          return utils.appendHeaders(operation, {
            Authorization: `Bearer ${token}`,
          });
        },
        didAuthError() {
          return false;
        },
        async refreshAuth() {},
      };
    }),
    fetchExchange,
    subscriptionExchange({
      forwardSubscription(request) {
        const input = { ...request, query: request.query || "" };

        return {
          subscribe(sink) {
            const unsubscribe = wsClient.subscribe(input, sink);
            return { unsubscribe };
          },
        };
      },
    }),
  ],
  fetchOptions: {},
});

export default client;
