import { PlaywrightTestArgs, TestFixture } from "@playwright/test";
import { Roles } from "../../../src/@types";

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
  TestFixture<AuthFixture, PlaywrightTestArgs>,
  {
    auto: boolean;
  },
] => [
  async ({ page }, use) => {
    const asRole = (role: Roles) => async () => {
      await page.goto(`/auth?token=${tokens[role]}`);
      await page.waitForTimeout(2000);
    };

    const asAdmin = asRole(Roles.Admin);
    const asUser = asRole(Roles.User);

    use({ asAdmin, asUser });
  },
  {
    auto: true,
  },
];
