import { expect, test } from "../../mocks/playwright";
import { getAllRooms, getVersion } from "../../mocks/queries";
import { ConnectionInitMessage } from "../../types";

import { Roles } from "../../../src/@types";
import { tokens } from "../../auth";

test.describe("Auth", () => {
  test.describe("using the authentication route", () => {
    test("uses the new token for authentication", async ({ worker, subscriptions, page }) => {
      worker.use(getAllRooms, getVersion);
      await page.goto(`/auth?token=${tokens[Roles.User]}`);
      await page.waitForTimeout(3000);

      expect(subscriptions.incoming).toHaveLength(2);

      const message = subscriptions.incoming[0] as ConnectionInitMessage;
      expect(message.type).toBe("connection_init");
      expect(message.payload).toHaveProperty("headers");
      expect(message.payload!.headers.Authorization).toBeDefined();
      expect(message.payload!.headers.Authorization).toBe(`Bearer ${tokens[Roles.User]}`);
    });
  });
});
