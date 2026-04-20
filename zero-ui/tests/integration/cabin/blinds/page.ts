import { SubscriptionInterceptor } from "@foundation-zero/graphql-subscriptions-mock";
import { Locator, Page } from "@playwright/test";
import { BlindsControl, Room } from "../../../../src/modules/domestic/types";
import allRooms from "../../../data/all-rooms";
import { ZeroSubscriptions } from "../../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class BlindsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionInterceptor<ZeroSubscriptions>,
  ) {}

  public open(): Promise<void> {
    return this.page.getByRole("tab").getByText("Blinds").click();
  }

  private get subscribeToRoom() {
    return this.subscriptions.subscribe("SubscribeToRoom");
  }

  public setBlindLevels(
    blindLevels: number[],
    room: Room = allRooms.rooms.find((room) => room.blinds.length === blindLevels.length)!,
  ): void {
    const blinds = room.blinds;

    this.subscribeToRoom.dispatch({
      rooms: [
        {
          ...room,
          blinds: blinds.map<BlindsControl>((blind, index) => ({
            ...blind,
            time: Date.now(),
            level: blindLevels[index] !== undefined ? blindLevels[index] : blind.level,
          })),
        },
      ],
    });
  }

  public get listItems(): Locator {
    return this.page.getByTestId("blinds-control");
  }

  public async textValues() {
    return (await this.page.getByTestId("blindsPosition").allTextContents()).map(Number);
  }
}
