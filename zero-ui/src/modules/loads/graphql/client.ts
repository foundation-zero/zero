import { useAuthStore } from "@/modules/domestic/stores/auth";
import { authExchange } from "@urql/exchange-auth";
import { cacheExchange, Client, fetchExchange, OperationContext } from "@urql/vue";

export const LOADS_CONTEXT: Pick<OperationContext, "url"> = {
  url: import.meta.env.VITE_LOADS_API_SERVER_URL,
};

const getHeaders = () => {
  const authStore = useAuthStore();
  const token = authStore.token ?? import.meta.env.VITE_GRAPHQL_TOKEN;

  return {
    Authorization: `Bearer ${token}`,
    "x-hasura-role": authStore.isAdmin ? "admin" : "user",
  };
};

const client = new Client({
  url: LOADS_CONTEXT.url,
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
  ],
  fetchOptions: {},
});

export default client;
