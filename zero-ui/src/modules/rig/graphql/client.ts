import { useAuthStore } from "@/modules/common/stores/auth";
import { ENV } from "@env";
import { authExchange } from "@urql/exchange-auth";
import { cacheExchange, Client, fetchExchange } from "@urql/vue";

const getHeaders = () => {
  const authStore = useAuthStore();
  const token = authStore.token ?? ENV.VITE_GRAPHQL_TOKEN;

  return {
    Authorization: `Bearer ${token}`,
    "x-hasura-role": authStore.isAdmin ? "admin" : "user",
  };
};

const client = new Client({
  // Rig reads the fiber optics variables that the loads app serves.
  url: ENV.VITE_LOADS_API_SERVER_URL,
  exchanges: [
    cacheExchange,
    authExchange(async (utils) => ({
      addAuthToOperation: (operation) => utils.appendHeaders(operation, getHeaders()),
      didAuthError: () => false,
      refreshAuth: async () => {},
    })),
    fetchExchange,
  ],
});

export default client;
