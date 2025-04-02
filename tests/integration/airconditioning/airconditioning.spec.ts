import allRooms from "../../data/all-rooms";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import AirconditioningPage from "./page";

const test = testBase.extend<{ aircoPage: AirconditioningPage }>({
  aircoPage: [
    async ({ page, worker, subscriptions }, use) => {
      worker.use(getAllRooms);

      await page.goto("/airco");
      await page.waitForTimeout(1000);
      await use(new AirconditioningPage(page, subscriptions));
    },
    { auto: true },
  ],
});

test.describe("Airconditioning", () => {
  const room = allRooms.rooms[0];
  test("shows the correct temperature", async ({ aircoPage }) => {
    const actualTemperature = 23.1;
    aircoPage.setInsideTemperature(room, actualTemperature);

    await expect(aircoPage.actualTemperature).toHaveText(actualTemperature.toString());
  });

  test("shows the correct setpoint", async ({ aircoPage }) => {
    const temperatureSetpoint = 25.3;
    aircoPage.setTemperatureSetpoint(room, temperatureSetpoint);

    await expect(aircoPage.temperatureSetpoint).toHaveText(`253°`);
  });
});
