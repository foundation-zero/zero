import { authExchange } from "@urql/exchange-auth";
import { cacheExchange, Client, fetchExchange } from "@urql/vue";

const client = new Client({
  url: `${import.meta.env.VITE_GRAPHQL_URL}`,
  exchanges: [
    cacheExchange,
    authExchange(async (utils) => {
      const token = import.meta.env.VITE_GRAPHQL_TOKEN;

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
  ],
  fetchOptions: {},
});

export default client;
