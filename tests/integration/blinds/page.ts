import { Locator, Page } from "@playwright/test";
import { Rooms } from "../../../src/gql/graphql";
import allRooms from "../../data/all-rooms";
import { ZeroSubscriptions } from "../../mocks/playwright";
import { SubscriptionFixture } from "../fixtures/graphql";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class BlindsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionFixture<ZeroSubscriptions>,
  ) {}

  public setBlindLevels(
    blindLevels: number[],
    room: Rooms = allRooms.rooms.find((room) => room.blinds.length === blindLevels.length)!,
  ): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [
        {
          ...room,
          blinds: room.blinds.map((blind, index) => ({
            ...blind,
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
    return await this.page.getByTestId("blindsPosition").allTextContents();
  }
}
