import { expect, test } from "../../mocks/playwright";
import { ConnectionInitMessage } from "../../types";

test.describe("App", () => {
  test("has correct title", async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    await expect(page).toHaveTitle(/Zero/);
  });

  test("connects to graphql server", async ({ page, subscriptions }) => {
    await page.goto("/");
    await page.waitForTimeout(1000);

    expect(subscriptions.incoming).toHaveLength(2);

    const message = subscriptions.incoming[0] as ConnectionInitMessage;
    expect(message.type).toBe("connection_init");
    expect(message.payload).toHaveProperty("headers");
    expect(message.payload!.headers.Authorization).toBeDefined();
    expect(message.payload!.headers.Authorization).toMatch(/Bearer [\w.-]+/);
  });
});
