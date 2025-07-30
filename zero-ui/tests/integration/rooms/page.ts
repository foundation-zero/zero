import { Locator, Page } from "@playwright/test";
import { SubscriptionInterceptor } from "graphql-subscriptions-mock";
import { Room } from "../../../src/@types";
import { SubscribeMessage } from "../../lib/types";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class RoomsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionInterceptor<ZeroSubscriptions>,
  ) {}

  private get subscribeToRoom() {
    return this.subscriptions.subscribe("SubscribeToRoom");
  }

  public updateRoom(room: Room, delta: Partial<Room> = {}): void {
    this.subscribeToRoom.dispatch({
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
    return this.subscribeToRoom.subscribers;
  }

  public get actualTemperature(): Locator {
    return this.page.locator("#actualTemperature");
  }

  public get temperatureSetpoint() {
    return this.page.getByTestId("temperatureSetpoint");
  }
}
