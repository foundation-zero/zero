import allRooms from "../../data/all-rooms";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import BlindsPage from "./page";

const test = testBase.extend<{ blindsPage: BlindsPage }>({
  blindsPage: [
    async ({ worker, page, subscriptions }, use) => {
      worker.use(getAllRooms);

      await page.goto("/blinds");
      await page.waitForTimeout(1000);
      await page.screenshot({ path: "screenshots/blinds.png" });
      await use(new BlindsPage(page, subscriptions));
    },
    { auto: true },
  ],
});

test.describe("Blinds", () => {
  test.describe("with 2 blinds", () => {
    const targetLevels = [0.51, 0.75];

    test.beforeEach(async ({ blindsPage }) => {
      blindsPage.setBlindLevels(targetLevels);
    });

    test("shows two controls", async ({ blindsPage }) => {
      await expect(blindsPage.listItems).toHaveCount(2);
    });

    test("shows the correct values", async ({ blindsPage }) => {
      expect(await blindsPage.textValues()).toEqual(
        targetLevels.map((level) => (level * 100).toString()),
      );
    });
  });

  test.describe("with > 2 blinds", () => {
    const room = allRooms.rooms.find((room) => room.blinds.length > 2)!;

    test.beforeEach(async ({ blindsPage }) => {
      blindsPage.setBlindLevels([], room);
    });
    test("shows the correct amount of controls", async ({ blindsPage }) => {
      await expect(blindsPage.listItems).toHaveCount(room.blinds.length);
    });

    test("does not show numeral values", async ({ blindsPage }) => {
      expect(await blindsPage.textValues()).toEqual([]);
    });

    test("shows a modal with controls", async ({ blindsPage }) => {
      await blindsPage.listItems.first().click();

      expect(await blindsPage.textValues()).toEqual(["0", "0"]);
    });
  });
});
