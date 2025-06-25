import { test as base, expect } from "@playwright/test";
import { graphql, http } from "msw";
import type { MockServiceWorker } from "playwright-msw";
import { createWorkerFixture } from "playwright-msw";
import { Room } from "../../src/@types";
import { AuthFixture, createAuthFixture } from "../integration/fixtures/auth";
import { createSubscriptionFixture, SubscriptionFixture } from "../integration/fixtures/graphql";
import { createSessionFixture, SessionFixture } from "../integration/fixtures/session";

export type ZeroSubscriptions = {
  SubscribeToRoom: { rooms: Room[] };
};

const test = base.extend<{
  worker: MockServiceWorker;
  http: typeof http;
  graphql: typeof graphql;
  subscriptions: SubscriptionFixture<ZeroSubscriptions>;
  auth: AuthFixture;
  session: SessionFixture;
}>({
  worker: createWorkerFixture([], { graphqlUrl: process.env.VITE_GRAPHQL_URL }),
  http,
  graphql,
  subscriptions: createSubscriptionFixture<ZeroSubscriptions>({
    url: process.env.VITE_GRAPHQL_WS_URL!,
    autoAck: true,
  }),
  auth: createAuthFixture(),
  session: createSessionFixture(),
});

export { expect, test };
