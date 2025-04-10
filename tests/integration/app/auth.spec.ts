import { expect, test } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import { ConnectionInitMessage } from "../../types";

test.describe("Auth", () => {
  test.describe("using the authentication route", () => {
    const token =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlByYXZlZW4gRHVyYWlyYWp1IiwiaWF0IjoxNTE2MjM5MDIyfQ.5hffgKYLre_YU4Cdgv7FUo4-LKiKooGKf3QnOMbM2gs";

    test("uses the new token for authentication", async ({ worker, subscriptions, page }) => {
      worker.use(getAllRooms);
      await page.goto(`/auth?token=${token}`);
      await page.waitForTimeout(1000);

      expect(subscriptions.incoming).toHaveLength(2);

      const message = subscriptions.incoming[0] as ConnectionInitMessage;
      expect(message.type).toBe("connection_init");
      expect(message.payload).toHaveProperty("headers");
      expect(message.payload!.headers.Authorization).toBeDefined();
      expect(message.payload!.headers.Authorization).toBe(`Bearer ${token}`);
    });
  });
});
