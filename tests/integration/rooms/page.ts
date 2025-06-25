import { Locator, Page } from "@playwright/test";
import { Room } from "../../../src/@types";
import { SubscribeMessage } from "../../lib/types";
import { ZeroSubscriptions } from "../../mocks/playwright";
import { SubscriptionFixture } from "../fixtures/graphql";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class RoomsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionFixture<ZeroSubscriptions>,
  ) {}

  public updateRoom(room: Room, delta: Partial<Room> = {}): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [{ ...room, ...delta }],
    });
  }

  public get trigger(): Locator {
    return this.page.getByTestId("room-selector-button");
  }

  public get title(): Locator {
    return this.page.getByTestId("room-name");
  }

  public get dialog(): Locator {
    return this.page.locator("aside");
  }

  public get roomList(): Locator {
    return this.dialog.locator("[role='list'] li");
  }

  public roomItem(roomId: string): Locator {
    return this.dialog.getByTestId(`room-${roomId}`);
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
