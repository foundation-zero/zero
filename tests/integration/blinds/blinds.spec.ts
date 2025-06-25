import { rooms } from "../../data/all-rooms";
import { isBlindsControl } from "../../lib/helpers";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms, getVersion } from "../../mocks/queries";
import BlindsPage from "./page";

const dutchCabin = rooms.find((room) => room.id === "dutch-cabin")!;

const test = testBase.extend<{ blindsPage: BlindsPage }>({
  blindsPage: [
    async ({ worker, page, subscriptions, auth }, use) => {
      worker.use(getAllRooms, getVersion);

      const blindsPage = new BlindsPage(page, subscriptions);

      await auth.asUser();

      blindsPage.setBlindLevels([0, 0], dutchCabin);
      await page.waitForTimeout(500);
      await blindsPage.open();

      await page.waitForTimeout(1000);

      await page.screenshot({ path: "screenshots/blinds.png" });

      await use(blindsPage);
    },
    { auto: true },
  ],
});

test.describe("Blinds", () => {
  const roomWithTwoBlinds = rooms.find(
    (room) => room.roomsControls.filter(isBlindsControl).length === 2,
  )!;

  test.describe("with 2 blinds", () => {
    const targetLevels = [0.51, 0.75];

    test.beforeEach(async ({ page, blindsPage }) => {
      blindsPage.setBlindLevels(targetLevels, {
        ...dutchCabin,
        roomsControls: roomWithTwoBlinds.roomsControls,
      });

      await page.waitForTimeout(500);
    });

    test("shows two controls", async ({ blindsPage }) => {
      await expect(blindsPage.listItems).toHaveCount(2);
    });

    test("shows the correct values", async ({ blindsPage }) => {
      await expect(blindsPage.listItems).toHaveCount(2);

      expect(await blindsPage.textValues()).toEqual(
        targetLevels.map((level) => (level * 100).toString()),
      );
    });
  });

  test.describe("with > 2 blinds", () => {
    const roomWithMoreThanTwoBlinds = rooms.find(
      (room) => room.roomsControls.filter(isBlindsControl).length > 2,
    )!;

    test.beforeEach(async ({ blindsPage }) => {
      blindsPage.setBlindLevels([], {
        ...dutchCabin,
        roomsControls: roomWithMoreThanTwoBlinds.roomsControls,
      });
    });

    test("shows the correct amount of controls", async ({ blindsPage }) => {
      await expect(blindsPage.listItems).toHaveCount(
        roomWithMoreThanTwoBlinds.roomsControls.filter(isBlindsControl).length,
      );
    });

    test("does not show numeral values", async ({ blindsPage }) => {
      expect(await blindsPage.textValues()).toEqual([]);
    });

    test("shows a modal with controls", async ({ blindsPage, page }) => {
      await blindsPage.listItems.first().click();
      await page.waitForTimeout(500);

      expect(await blindsPage.textValues()).toEqual(["0", "0"]);
    });
  });
});
