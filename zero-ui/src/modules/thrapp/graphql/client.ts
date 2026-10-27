import { ENV } from "@env";
import { Client, fetchExchange, OperationContext } from "@urql/vue";

export const context: Partial<OperationContext> = {
  url: ENV.VITE_THRS_API_SERVER_URL ?? "/api/thrs/graphql",
};

export const client = new Client({
  url: context.url!,
  exchanges: [fetchExchange],
});
