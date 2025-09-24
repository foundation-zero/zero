import { expect, test as testBase } from "../../../mocks/playwright";
import THRSPage from "./page";

const test = testBase.extend<{ thrsPage: THRSPage }>({
  thrsPage: [
    async ({ page }, use) => {
      const thrsPage = new THRSPage(page);

      await use(thrsPage);
    },
    { auto: true },
  ],
});

test.describe("THRS App", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/thrs/overview");
  });

  test("has correct title", async ({ page }) => {
    await expect(page).toHaveTitle(/Zero/);
  });

  test("has a top navigation", async ({ thrsPage }) => {
    await expect(thrsPage.navigation).toBeVisible();
  });
  test("has action buttons", async ({ thrsPage }) => {
    await expect(thrsPage.actions).toBeVisible();
  });
  test("has breadcrumbs", async ({ thrsPage }) => {
    await expect(thrsPage.breadcrumbs).toBeVisible();
  });
});
