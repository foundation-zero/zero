import { ConnectionInitMessage } from "../../lib/types";
import { expect, test } from "../../mocks/playwright";
import { getAllRooms, getVersion } from "../../mocks/queries";

test.describe("App", () => {
  test.beforeEach(async ({ worker, page, auth }) => {
    worker.use(getAllRooms, getVersion);
    await page.goto("/");
    await auth.asUser();
  });

  test("has correct title", async ({ page }) => {
    await page.screenshot({ path: "screenshots/app.png" });
    await expect(page).toHaveTitle(/Zero/);
  });

  test("connects to graphql server", async ({ subscriptions }) => {
    expect(subscriptions.incoming).toHaveLength(2);

    const message = subscriptions.incoming[0] as ConnectionInitMessage;
    expect(message.type).toBe("connection_init");
    expect(message.payload).toHaveProperty("headers");
    expect(message.payload!.headers.Authorization).toBeDefined();
    expect(message.payload!.headers.Authorization).toMatch(/Bearer [\w.-]+/);
  });
});
