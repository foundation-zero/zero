import allRooms from "../../data/all-rooms";
import { setLightLevel } from "../../mocks/mutations";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms, getControlLogs, getSensorLogs, getVersion } from "../../mocks/queries";
import LightsPage from "./page";

const dutchCabin = allRooms.rooms.find((room) => room.id === "dutch-cabin")!;

const test = testBase.extend<{ lightsPage: LightsPage }>({
  lightsPage: [
    async ({ page, worker, subscriptions, auth }, use) => {
      worker.use(getAllRooms, setLightLevel, getVersion, getSensorLogs, getControlLogs);

      const lightsPage = new LightsPage(page, subscriptions);
      await auth.asUser();
      lightsPage.setLightLevels([0, 0], dutchCabin);
      await lightsPage.open();
      await page.waitForTimeout(500);

      await page.screenshot({ path: "screenshots/lights_before.png" });
      await use(lightsPage);
    },
    { auto: true },
  ],
});

test.describe("Lights", () => {
  test.describe("with multiple lights", () => {
    const targetLevels = [0.51, 0.75];
    test.beforeEach(async ({ lightsPage, page }) => {
      lightsPage.setLightLevels(targetLevels, dutchCabin);
      await page.screenshot({ path: "screenshots/lights_after.png" });
    });

    test("shows controls for each light", async ({ lightsPage }) => {
      await expect(lightsPage.sliders).toHaveCount(2);
    });

    test("shows the correct values", async ({ lightsPage }) => {
      const firstValue = await lightsPage.getValue(0);
      const secondValue = await lightsPage.getValue(1);

      expect(firstValue).toBe((targetLevels[0] * 100).toString());
      expect(secondValue).toBe((targetLevels[1] * 100).toString());
    });
  });

  test.describe("changing the light level", () => {
    const targetLevels = [0.51, 0.75];

    test.beforeEach(async ({ lightsPage }) => {
      lightsPage.setLightLevels(targetLevels, dutchCabin);
    });

    test("pushes a mutation", async ({ lightsPage, page }) => {
      const track = lightsPage.tracks.first();

      await track.click({ position: { x: 300, y: 0 } });

      await page.waitForTimeout(1000);
      expect(setLightLevel.isUsed).toBe(true);
    });
  });

  test.describe("toggle light", () => {
    test.describe("when light is off", () => {
      test.beforeEach(async ({ lightsPage }) => {
        lightsPage.setLightLevels([0, 0], dutchCabin);

        await lightsPage.switches.first().click();
      });

      test("turns the light on", async ({ lightsPage }) => {
        const value = await lightsPage.getValue(0);

        expect(value).toBe("100");
      });

      test("pushes a mutation", async ({ page }) => {
        await page.waitForTimeout(1000);
        expect(setLightLevel.isUsed).toBe(true);
      });
    });

    test.describe("when light is on", () => {
      test.beforeEach(async ({ lightsPage, page }) => {
        lightsPage.setLightLevels([0.1, 0.1], dutchCabin);

        await page.waitForTimeout(1000);

        await lightsPage.switches.first().click();

        await page.waitForTimeout(1000);
      });

      test("turns the light off", async ({ lightsPage }) => {
        const value = await lightsPage.getValue(0);

        expect(value).toBe("0");
      });

      test("pushes a mutation", async ({ page }) => {
        await page.waitForTimeout(1000);
        expect(setLightLevel.isUsed).toBe(true);
      });
    });
  });
});
