import { Locator, Page } from "@playwright/test";
import { SubscriptionInterceptor } from "graphql-subscriptions-mock";
import { Room } from "../../../src/@types";
import { toTemperatureControl, toTemperatureSensor } from "../../lib/helpers";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class AirconditioningPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionInterceptor<ZeroSubscriptions>,
  ) {}

  private get subscribeToRoom() {
    return this.subscriptions.subscribe("SubscribeToRoom");
  }

  public setTemperatureSetpoint(room: Room, temperatureSetpoint: number): void {
    this.subscribeToRoom.dispatch({
      rooms: [
        {
          ...room,
          roomsControls: [toTemperatureControl(temperatureSetpoint)],
        },
      ],
    });
  }

  public setInsideTemperature(room: Room, temperature: number): void {
    this.subscribeToRoom.dispatch({
      rooms: [
        {
          ...room,
          roomsSensors: [toTemperatureSensor(temperature)],
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
