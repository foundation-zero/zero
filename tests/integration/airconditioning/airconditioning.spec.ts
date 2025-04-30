import allRooms from "../../data/all-rooms";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import AirconditioningPage from "./page";

const dutchCabin = allRooms.rooms.find((room) => room.id === "dutch-cabin")!;

const test = testBase.extend<{ aircoPage: AirconditioningPage }>({
  aircoPage: [
    async ({ page, worker, subscriptions, auth }, use) => {
      worker.use(getAllRooms);

      const aircoPage = new AirconditioningPage(page, subscriptions);
      await auth.asUser();

      aircoPage.setInsideTemperature(dutchCabin, dutchCabin.actualTemperature);
      await page.waitForTimeout(1000);

      await page.screenshot({ path: "screenshots/airconditioning.png" });
      await use(aircoPage);
    },
    { auto: true },
  ],
});

test.describe("Airconditioning", () => {
  test("shows the correct temperature", async ({ aircoPage }) => {
    const actualTemperature = 23.1;
    aircoPage.setInsideTemperature(dutchCabin, actualTemperature);

    await expect(aircoPage.actualTemperature).toHaveText(actualTemperature.toString());
  });

  test("shows the correct setpoint", async ({ aircoPage }) => {
    const temperatureSetpoint = 25.3;
    aircoPage.setTemperatureSetpoint(dutchCabin, temperatureSetpoint);

    await expect(aircoPage.temperatureSetpoint).toHaveText(`253°`);
  });
});
