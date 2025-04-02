import { Locator, Page } from "@playwright/test";
import { Rooms } from "../../../src/gql/graphql";
import { SubscriptionFixture } from "../../mocks/graphql";
import { ZeroSubscriptions } from "../../mocks/playwright";
import { SubscribeMessage } from "../../types";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class RoomsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionFixture<ZeroSubscriptions>,
  ) {}

  public updateRoom(room: Rooms, delta: Partial<Rooms> = {}): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [{ ...room, ...delta }],
    });
  }

  public get trigger(): Locator {
    return this.page.getByTestId("room-selector-button");
  }

  public get dialog(): Locator {
    return this.page.getByRole("dialog");
  }

  public get roomList(): Locator {
    return this.page.getByRole("dialog").locator("li");
  }

  public roomItem(roomId: string): Locator {
    return this.page.getByRole("dialog").getByTestId(roomId);
  }

  public get audioSystemToggle(): Locator {
    return this.page.getByTestId("av-toggle");
  }

  public get subscribers(): SubscribeMessage[] {
    return this.subscriptions.subscribers("SubscribeToRoom");
  }

  public get actualTemperature(): Locator {
    return this.page.locator("#actualTemperature");
  }

  public get temperatureSetpoint() {
    return this.page.getByTestId("temperatureSetpoint");
  }
}
