import { ENV } from "@env";
import { Client, fetchExchange, OperationContext } from "@urql/vue";

// The monitoring API: history from GreptimeDB and the crew's annotations. It ran in
// thrs-api, which is gone; docs/adr/0003-thrs-monitoring-api.md proposes where it runs.
export const context: Partial<OperationContext> = {
  url: ENV.VITE_THRS_MONITORING_API_SERVER_URL ?? "/api/thrs-monitoring/graphql",
};

export const client = new Client({
  url: context.url!,
  exchanges: [fetchExchange],
});
