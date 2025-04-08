import { test as base, expect } from "@playwright/test";
import { graphql, http } from "msw";
import type { MockServiceWorker } from "playwright-msw";
import { createWorkerFixture } from "playwright-msw";
import { Rooms } from "../../src/gql/graphql";
import { createSubscriptionFixture, SubscriptionFixture } from "./graphql";

export type ZeroSubscriptions = {
  SubscribeToRoom: { rooms: Rooms[] };
};

const test = base.extend<{
  worker: MockServiceWorker;
  http: typeof http;
  graphql: typeof graphql;
  subscriptions: SubscriptionFixture<ZeroSubscriptions>;
}>({
  worker: createWorkerFixture([], { graphqlUrl: process.env.VITE_GRAPHQL_URL }),
  http,
  graphql,
  subscriptions: createSubscriptionFixture<ZeroSubscriptions>({
    url: process.env.VITE_GRAPHQL_WS_URL!,
    autoAck: true,
  }),
});

export { expect, test };
