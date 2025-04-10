import { useAuthStore } from "@/stores/auth";
import { authExchange } from "@urql/exchange-auth";
import { cacheExchange, Client, fetchExchange, subscriptionExchange } from "@urql/vue";

import { createClient as createWSClient } from "graphql-ws";

const getHeaders = () => {
  const authStore = useAuthStore();
  const token = authStore.token ?? import.meta.env.VITE_GRAPHQL_TOKEN;

  return {
    Authorization: `Bearer ${token}`,
    "x-hasura-role": authStore.isAdmin ? "admin" : "user",
  };
};

const wsClient = createWSClient({
  url: `${import.meta.env.VITE_GRAPHQL_WS_URL}`,

  connectionParams: () => {
    return {
      headers: getHeaders(),
    };
  },
});

const client = new Client({
  url: `${import.meta.env.VITE_GRAPHQL_URL}`,
  exchanges: [
    cacheExchange,
    authExchange(async (utils) => {
      return {
        addAuthToOperation(operation) {
          return utils.appendHeaders(operation, getHeaders());
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
