import { expect, test } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import { ConnectionInitMessage } from "../../types";

test.describe("Auth", () => {
  test.describe("using the authentication route", () => {
    const token =
      "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImNlMTdlMWQ2MGY5YTBkODRmOTA2YmVhZGRlYjkxYTBhIn0.eyJodHRwczovL2hhc3VyYS5pby9qd3QvY2xhaW1zIjp7IngtaGFzdXJhLWRlZmF1bHQtcm9sZSI6InVzZXIiLCJ4LWhhc3VyYS1hbGxvd2VkLXJvbGVzIjpbInVzZXIiXSwieC1oYXN1cmEtY2FiaW4iOiJkdXRjaC1jYWJpbiJ9fQ.ITbZpZczKw7HnS2zmp2bcgYFmszWizS_1GGVTylzKowliktF57P-4wCOJo9gEJszWYRTm9AZWB6LnxI4ENThIw";

    test("uses the new token for authentication", async ({ worker, subscriptions, page }) => {
      worker.use(getAllRooms);
      await page.goto(`/auth?token=${token}`);
      await page.waitForTimeout(3000);

      expect(subscriptions.incoming).toHaveLength(2);

      const message = subscriptions.incoming[0] as ConnectionInitMessage;
      expect(message.type).toBe("connection_init");
      expect(message.payload).toHaveProperty("headers");
      expect(message.payload!.headers.Authorization).toBeDefined();
      expect(message.payload!.headers.Authorization).toBe(`Bearer ${token}`);
    });
  });
});
