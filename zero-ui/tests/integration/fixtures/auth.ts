import { SubscriptionInterceptor } from "@foundation-zero/graphql-subscriptions-mock";
import { expect, PlaywrightTestArgs, TestFixture } from "@playwright/test";
import { Roles } from "../../../src/modules/common/types";
import type { ZeroSubscriptions } from "../../mocks/playwright";

export interface AuthFixture {
  asAdmin(): Promise<void>;
  asUser(): Promise<void>;
}

const tokens: Record<Roles, string> = {
  [Roles.Admin]:
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImNlMTdlMWQ2MGY5YTBkODRmOTA2YmVhZGRlYjkxYTBhIn0.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbInVzZXIiLCJhZG1pbiJdfX0.cPDZfwzO8fnrEZPZrW3kdtiGWiUvD680fsqTgyoZCS-GPO5787cJFTA0koRkIuE8lLA5aS-lCtb4I2wPBv11-A",
  [Roles.User]:
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbInVzZXIiXSwieC1oYXN1cmEtY2FiaW4iOiJkdXRjaC1jYWJpbiJ9fQ.XZ3tGElMxyN9l_nlKpKK0lKoNa6BEHXvx8HRgSgLFKU",
};

export const createAuthFixture = (): [
  TestFixture<
    AuthFixture,
    PlaywrightTestArgs & { subscriptions: SubscriptionInterceptor<ZeroSubscriptions> }
  >,
  {
    auto: boolean;
  },
] => [
  async ({ page, subscriptions }, use) => {
    const asRole = (role: Roles) => async () => {
      await page.goto(`/domestic/auth?token=${tokens[role]}`);
      // The auth route redirects once the token is verified; the app then subscribes to the
      // rooms, after which tests can dispatch room data.
      await page.waitForURL((url) => !url.pathname.endsWith("/auth"));
      await expect
        .poll(() => subscriptions.subscribe("SubscribeToRooms").subscribers.length)
        .toBeGreaterThan(0);
    };

    const asAdmin = asRole(Roles.Admin);
    const asUser = asRole(Roles.User);

    await use({ asAdmin, asUser });
  },
  {
    auto: true,
  },
];
