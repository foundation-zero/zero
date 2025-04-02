import { Locator, Page } from "@playwright/test";
import { Rooms } from "../../../src/gql/graphql";
import { SubscriptionFixture } from "../../mocks/graphql";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class AirconditioningPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionFixture<ZeroSubscriptions>,
  ) {}

  public setTemperatureSetpoint(room: Rooms, temperatureSetpoint: number): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [
        {
          ...room,
          temperatureSetpoint,
        },
      ],
    });
  }

  public setInsideTemperature(room: Rooms, temperature: number): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [
        {
          ...room,
          actualTemperature: temperature,
        },
      ],
    });
  }

  public get actualTemperature(): Locator {
    return this.page.locator("#actualTemperature");
  }

  public get temperatureSetpoint() {
    return this.page.getByTestId("temperatureSetpoint");
  }
}
