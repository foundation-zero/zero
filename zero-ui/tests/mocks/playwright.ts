import { SubscriptionInterceptor } from "@foundation-zero/graphql-subscriptions-mock";
import { createSubscriptionFixture } from "@foundation-zero/graphql-subscriptions-mock/adapters/playwright";
import { defineNetworkFixture, type NetworkFixture } from "@msw/playwright";
import { test as base, expect } from "@playwright/test";
import { http } from "msw";
import { graphql } from "msw/graphql";
import { Room } from "../../src/@types";
import { AuthFixture, createAuthFixture } from "../integration/fixtures/auth";
import { createSessionFixture, SessionFixture } from "../integration/fixtures/session";

export type ZeroSubscriptions = {
  SubscribeToRoom: { rooms: Room[] };
};

const test = base.extend<{
  worker: NetworkFixture;
  http: typeof http;
  graphql: typeof graphql;
  subscriptions: SubscriptionInterceptor<ZeroSubscriptions>;
  auth: AuthFixture;
  session: SessionFixture;
}>({
  worker: async ({ context }, use) => {
    const network = defineNetworkFixture({ context, onUnhandledFrame: "bypass" });
    await network.enable();
    await use(network);
    await network.disable();
  },
  http,
  graphql,
  subscriptions: createSubscriptionFixture<ZeroSubscriptions>(process.env.VITE_GRAPHQL_WS_URL!),
  auth: createAuthFixture(),
  session: createSessionFixture(),
});

export { expect, test };
