import { Client, fetchExchange, OperationContext } from "@urql/vue";

export const context: Partial<OperationContext> = {
  url: "/api/thrs/graphql",
};

export const client = new Client({
  url: context.url!,
  exchanges: [fetchExchange],
});
